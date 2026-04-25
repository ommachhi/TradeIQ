"""
Django REST API Views for Stock Price Prediction

Handles prediction requests, user management, and all backend functionality
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.db.models import Count, Avg, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from pathlib import Path
import pandas as pd
import os
import uuid
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from .symbols import resolve_symbol_with_history

from .serializers import (
    PredictionSerializer,
    PredictionResponseSerializer,
    HistoryDataSerializer,
    StockHistorySerializer,
    StockDataSerializer,
    PortfolioSerializer,
    UserSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    DatasetSerializer,
    ModelHistorySerializer,
    PredictionHistorySerializer,
    ActivityLogSerializer,
    UserManagementSerializer,
    RetrainModelSerializer,
    ResearchQuerySerializer,
    PDFReportSerializer
)
from .models import Dataset, ModelHistory, PredictionHistory, ActivityLog, UserProfile, Portfolio
from .research import build_research_panel
# Import ml_model only when needed to avoid startup issues
# from .ml_model import StockPricePredictor, stock_predictor

User = get_user_model()


def api_success(data=None, http_status=status.HTTP_200_OK):
    return Response({'success': True, 'data': data or {}, 'error': ''}, status=http_status)


def api_error(message, http_status=status.HTTP_400_BAD_REQUEST, data=None):
    return Response({'success': False, 'data': data or {}, 'error': message}, status=http_status)


def _get_user_role(user, default='investor'):
    try:
        return user.userprofile.role
    except UserProfile.DoesNotExist:
        return default


def _get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _log_activity(user, action, request=None, role=None):
    try:
        ActivityLog.objects.create(
            user=user,
            action=action,
            role=role or _get_user_role(user),
            ip_address=_get_client_ip(request) if request else None,
            user_agent=(request.META.get('HTTP_USER_AGENT', '')[:1000] if request else '')
        )
    except Exception:
        pass


def _ensure_active_model_history():
    active_model = ModelHistory.objects.filter(is_active=True).order_by('-training_date').first()
    if active_model:
        return active_model

    latest_model = ModelHistory.objects.order_by('-training_date').first()
    if latest_model:
        latest_model.is_active = True
        latest_model.save(update_fields=['is_active'])
    return latest_model


# Authentication Views
class RegisterView(APIView):
    """User registration endpoint"""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            _log_activity(user, "User registered", request=request)

            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User login endpoint"""

    permission_classes = [AllowAny]

    def post(self, request):
        identifier = (request.data.get('username') or request.data.get('email') or '').strip()
        password = request.data.get('password') or ''

        if not identifier or not password:
            return Response(
                {'error': 'Username/email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        matching_users = User.objects.filter(
            Q(username__iexact=identifier) | Q(email__iexact=identifier)
        ).order_by('date_joined', 'id')

        if not matching_users.exists():
            return Response(
                {'error': 'User account not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if matching_users.count() > 1:
            return Response(
                {'error': 'Duplicate account detected for this login identifier. Please contact admin.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        target_user = matching_users.first()
        if not target_user.is_active:
            return Response(
                {'error': 'This account has been blocked by admin'},
                status=status.HTTP_403_FORBIDDEN
            )

        user = authenticate(username=target_user.username, password=password)
        if not user:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        _log_activity(user, "User logged in", request=request)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class ProfileView(APIView):
    """User profile management"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        # Update user basic info
        user_serializer = UserSerializer(request.user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()

            # Update profile if role is provided
            if 'role' in request.data:
                try:
                    profile = request.user.userprofile
                    profile.role = request.data['role']
                    profile.save()
                except UserProfile.DoesNotExist:
                    UserProfile.objects.create(user=request.user, role=request.data['role'])

            # Log activity
            try:
                profile = request.user.userprofile
                ActivityLog.objects.create(
                    user=request.user,
                    action="Profile updated",
                    role=profile.role
                )
            except UserProfile.DoesNotExist:
                ActivityLog.objects.create(
                    user=request.user,
                    action="Profile updated",
                    role='investor'
                )

            return Response(UserSerializer(request.user).data)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Prediction Views
class PredictionAPIView(APIView):
    """Stock price prediction endpoint"""

    permission_classes = [IsAuthenticated]

    def _run_prediction(self, data, user):
        # Import ML predictor lazily to keep startup resilient.
        from ai.predictor import make_prediction

        result = make_prediction(data)
        recommendation = result.get('recommendation')
        if recommendation not in {'BUY', 'SELL', 'HOLD'}:
            recommendation = (
                'BUY' if result.get('trend') == 'UP'
                else 'SELL' if result.get('trend') == 'DOWN'
                else 'HOLD'
            )
        # save to history
        try:
            PredictionHistory.objects.create(
                user=user,
                stock_symbol=result.get('symbol', ''),
                open_price=data.get('open', 0),
                high_price=data.get('high', 0),
                low_price=data.get('low', 0),
                close_price=data.get('close', 0),
                volume=data.get('volume', 0),
                predicted_price=result.get('predicted_price'),
                recommendation=recommendation,
            )
        except Exception:
            pass
        result['recommendation'] = recommendation
        return result

    def post(self, request):
        try:
            # Validate input data
            serializer = PredictionSerializer(data=request.data)

            if not serializer.is_valid():
                details = serializer.errors
                default_message = 'Invalid stock symbol. Please enter a valid symbol like AAPL, RELIANCE.NS, TCS.NS'
                message = default_message
                if isinstance(details, dict):
                    non_field = details.get('non_field_errors')
                    if non_field and isinstance(non_field, list) and non_field[0]:
                        message = str(non_field[0])
                return api_error(message, http_status=status.HTTP_400_BAD_REQUEST, data={'details': details})

            validated_data = serializer.validated_data

            # run prediction
            result = self._run_prediction(validated_data, request.user)
            return api_success(result)

        except TimeoutError:
            return api_error('Prediction request timed out. Please try again.', http_status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception:
            return api_error('Prediction failed. Please try again.', http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        # allow GET /api/predict/?symbol=AAPL for convenience
        symbol = request.query_params.get('symbol')
        if not symbol:
            return api_error('Symbol query parameter required', http_status=status.HTTP_400_BAD_REQUEST)
        validated = {'symbol': symbol}
        serializer = PredictionSerializer(data=validated)
        if not serializer.is_valid():
            details = serializer.errors
            message = 'Invalid stock symbol. Please enter a valid symbol like AAPL, RELIANCE.NS, TCS.NS'
            if isinstance(details, dict):
                non_field = details.get('non_field_errors')
                if non_field and isinstance(non_field, list) and non_field[0]:
                    message = str(non_field[0])
            return api_error(message, http_status=status.HTTP_400_BAD_REQUEST, data={'details': details})
        return api_success(self._run_prediction(serializer.validated_data, request.user))


class StockHistoryAPIView(APIView):
    """Historical stock data for charts.
    This endpoint is read-only and safe for anyone, so do not require login.
    """

    permission_classes = [AllowAny]  # allow anonymous users to fetch history

    def get(self, request):
        symbol = request.query_params.get('symbol', 'AAPL')
        period = request.query_params.get('period', '1y')

        try:
            # Validate symbol
            if not symbol or len(symbol) > 20:
                return api_error('Invalid stock symbol. Please enter a valid symbol like AAPL, RELIANCE.NS, TCS.NS', http_status=status.HTTP_400_BAD_REQUEST)

            # Fetch data from Yahoo Finance with NSE/BSE fallback for Indian symbols.
            resolved_symbol, hist = resolve_symbol_with_history(symbol, period=period)

            if hist is None or hist.empty:
                return api_error('Invalid stock symbol. Please enter a valid symbol like AAPL, RELIANCE.NS, TCS.NS', http_status=status.HTTP_404_NOT_FOUND)

            # Format data for charts
            data = []
            for date, row in hist.iterrows():
                date_str = date.strftime('%Y-%m-%d')
                data.append({
                    'time': date_str,
                    'date': date_str,
                    'close': round(float(row['Close']), 2)
                })

            return api_success({
                'symbol': resolved_symbol,
                'period': period,
                'data': data
            })

        except TimeoutError:
            return api_error('Invalid stock symbol or timeout', http_status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception:
            return api_error('Failed to fetch stock data.', http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Stock lookup endpoint

class StockAPIView(APIView):
    """Return recent OHLCV data for a symbol"""

    permission_classes = [AllowAny]

    def get(self, request):
        serializer = StockDataSerializer(data=request.query_params)
        if not serializer.is_valid():
            details = serializer.errors
            message = 'Invalid stock symbol. Please enter a valid symbol like AAPL, RELIANCE.NS, TCS.NS'
            if isinstance(details, dict):
                symbol_error = details.get('symbol')
                if symbol_error and isinstance(symbol_error, list) and symbol_error[0]:
                    message = str(symbol_error[0])
            return api_error(message, http_status=status.HTTP_400_BAD_REQUEST, data={'details': details})
        symbol = serializer.validated_data['symbol']
        period = serializer.validated_data.get('period', '1d')
        try:
            resolved_symbol, hist = resolve_symbol_with_history(symbol, period=period)
            if hist is None or hist.empty:
                return api_error(
                    'Invalid stock symbol. Please enter a valid symbol like AAPL, RELIANCE.NS, TCS.NS',
                    http_status=status.HTTP_404_NOT_FOUND
                )
            data = []
            for date, row in hist.iterrows():
                date_str = date.strftime('%Y-%m-%d')
                data.append({
                    'time': date_str,
                    'date': date_str,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume']),
                })
            return api_success({'symbol': resolved_symbol, 'period': period, 'data': data})
        except TimeoutError:
            return api_error('Invalid stock symbol or timeout', http_status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception:
            return api_error('Failed to fetch stock data.', http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResearchPanelAPIView(APIView):
    """Return a unified research payload for a symbol."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ResearchQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            details = serializer.errors
            message = 'Invalid stock symbol. Please enter a valid symbol like AAPL, RELIANCE.NS, TCS.NS'
            if isinstance(details, dict):
                symbol_error = details.get('symbol')
                range_error = details.get('range')
                if symbol_error and isinstance(symbol_error, list) and symbol_error[0]:
                    message = str(symbol_error[0])
                elif range_error and isinstance(range_error, list) and range_error[0]:
                    message = str(range_error[0])
            return api_error(message, http_status=status.HTTP_400_BAD_REQUEST, data={'details': details})

        symbol = serializer.validated_data['symbol']
        range_key = serializer.validated_data['range']

        try:
            payload = build_research_panel(symbol, range_key)
            return api_success(payload)
        except LookupError:
            return api_error('Unable to load research data for this symbol.', http_status=status.HTTP_404_NOT_FOUND)
        except TimeoutError:
            return api_error('Research request timed out. Please try again.', http_status=status.HTTP_504_GATEWAY_TIMEOUT)
        except ValueError as exc:
            return api_error(str(exc), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return api_error('Failed to build research panel.', http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Admin Views
class PortfolioAPIView(APIView):
    """Manage user portfolio"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        entries = Portfolio.objects.filter(user=request.user)
        serializer = PortfolioSerializer(entries, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = PortfolioSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserManagementAPIView(APIView):
    """Admin user management"""

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]  # Allow all authenticated users to view
        return [IsAuthenticated()]  # Could add IsAdminUser permission

    def get(self, request):
        try:
            profile = request.user.userprofile
            if profile.role != 'admin':
                return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

        users = User.objects.select_related('userprofile').all().order_by('date_joined', 'id')
        serializer = UserManagementSerializer(users, many=True)
        return Response(serializer.data)

    def patch(self, request, pk=None):
        try:
            profile = request.user.userprofile
            if profile.role != 'admin':
                return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(pk=pk)
            if user.pk == request.user.pk and request.data.get('is_active') is False:
                return Response(
                    {'error': 'You cannot block your own admin account'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = UserManagementSerializer(user, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                action = f"Updated user {user.username}"
                if 'is_active' in request.data:
                    action = f"{'Unblocked' if user.is_active else 'Blocked'} user {user.username}"
                _log_activity(request.user, action, request=request)

                return Response(serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk=None):
        try:
            profile = request.user.userprofile
            if profile.role != 'admin':
                return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

        if pk is None:
            return Response({'error': 'User id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.pk == request.user.pk:
            return Response(
                {'error': 'You cannot delete your own admin account'},
                status=status.HTTP_400_BAD_REQUEST
            )

        username = user.username
        user.delete()
        _log_activity(request.user, f"Deleted user {username}", request=request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DatasetManagementAPIView(APIView):
    """Dataset upload and management"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.userprofile
            if profile.role not in ['admin', 'researcher']:
                return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)

        datasets = Dataset.objects.all()
        serializer = DatasetSerializer(datasets, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            profile = request.user.userprofile
            if profile.role not in ['admin', 'researcher']:
                return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)

        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read and validate CSV
            df = pd.read_csv(file_obj)
            row_count, column_count = df.shape

            # Save file
            file_name = f"{uuid.uuid4()}_{file_obj.name}"
            file_path = os.path.join('datasets', file_name)
            file_obj.seek(0)
            default_storage.save(file_path, ContentFile(file_obj.read()))

            # Create dataset record
            dataset = Dataset.objects.create(
                name=request.data.get('name', file_obj.name),
                file=file_path,
                uploaded_by=request.user,
                row_count=row_count,
                column_count=column_count
            )

            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action=f"Uploaded dataset {dataset.name}",
                role=_get_user_role(request.user)
            )

            serializer = DatasetSerializer(dataset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': 'Failed to process dataset', 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ModelRetrainingAPIView(APIView):
    """Model retraining endpoint"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            profile = request.user.userprofile
            if profile.role != 'admin':
                return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

        serializer = RetrainModelSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        dataset_id = serializer.validated_data.get('dataset_id')
        model_name = serializer.validated_data.get('model_name')
        dataset = None

        try:
            from .ml_model import StockPricePredictor

            # Get dataset
            if dataset_id:
                dataset = Dataset.objects.get(id=dataset_id)
                dataset_path = dataset.file.path
            else:
                # Use default dataset
                dataset_path = str(Path(__file__).resolve().parents[1] / 'TradeIQ_stock_data.csv')

            if not os.path.exists(dataset_path):
                return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)

            # Train model
            training_result = StockPricePredictor.train_model(dataset_path, model_name)

            ModelHistory.objects.filter(is_active=True).update(is_active=False)

            # Save model history
            model_history = ModelHistory.objects.create(
                name=training_result['model_name'],
                model_file=training_result['model_path'],
                rmse=training_result['test_rmse'],
                r_squared=training_result['test_r2'],
                train_rmse=training_result['train_rmse'],
                train_r_squared=training_result['train_r2'],
                overfit_gap=training_result['overfit_gap'],
                feature_count=training_result['feature_count'],
                training_samples=training_result['training_samples'],
                testing_samples=training_result['testing_samples'],
                dataset_used=dataset if dataset_id else None,
                is_active=True,
            )

            try:
                from ai import predictor

                predictor._model = None
                predictor._scaler = None
                predictor._target_scaler = None
            except Exception:
                pass

            # Log activity
            _log_activity(request.user, f"Retrained model {model_name}", request=request)

            return Response({
                'message': 'Model retrained successfully',
                'model': ModelHistorySerializer(model_history).data,
                'metrics': {
                    'train_rmse': training_result['train_rmse'],
                    'rmse': training_result['test_rmse'],
                    'train_r_squared': training_result['train_r2'],
                    'r_squared': training_result['test_r2'],
                    'overfit_gap': training_result['overfit_gap'],
                    'training_samples': training_result['training_samples'],
                    'testing_samples': training_result['testing_samples'],
                }
            })

        except Exception as e:
            return Response(
                {'error': 'Retraining failed', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ModelHistoryAPIView(APIView):
    """Model history and performance"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.userprofile
            if profile.role not in ['admin', 'researcher']:
                return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)

        _ensure_active_model_history()
        models = ModelHistory.objects.all().order_by('-is_active', '-training_date')
        serializer = ModelHistorySerializer(models, many=True)
        return Response(serializer.data)


class PredictionHistoryAPIView(APIView):
    """Prediction history for users"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Users can see their own predictions, admins and staff can see all
        try:
            profile = request.user.userprofile
            if profile.role in ['admin', 'researcher', 'analyst']:
                predictions = PredictionHistory.objects.all()
            else:
                predictions = PredictionHistory.objects.filter(user=request.user)
        except UserProfile.DoesNotExist:
            predictions = PredictionHistory.objects.filter(user=request.user)

        predictions = predictions.order_by('-created_at')[:100]  # Limit to last 100
        serializer = PredictionHistorySerializer(predictions, many=True)
        return Response(serializer.data)


class ActivityLogAPIView(APIView):
    """Activity logs for admin and analyst"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.userprofile
            if profile.role not in ['admin', 'analyst']:
                return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

        logs = ActivityLog.objects.all().order_by('-timestamp')[:500]  # Last 500 logs
        serializer = ActivityLogSerializer(logs, many=True)
        return Response(serializer.data)


class PDFReportAPIView(APIView):
    """Generate PDF reports"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        prediction_id = request.query_params.get('prediction_id')

        if not prediction_id:
            return Response({'error': 'prediction_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get prediction
            prediction = PredictionHistory.objects.get(id=prediction_id)

            # Check permissions
            user_role = _get_user_role(request.user)
            if user_role not in ['admin', 'analyst'] and prediction.user != request.user:
                return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

            # Generate PDF
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter

            # Title
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, height - 50, "TradeIQ Stock Prediction Report")

            # Prediction details
            p.setFont("Helvetica", 12)
            y = height - 100

            p.drawString(100, y, f"Stock Symbol: {prediction.stock_symbol}")
            y -= 20
            p.drawString(100, y, f"Date: {prediction.created_at.strftime('%Y-%m-%d %H:%M')}")
            y -= 20
            p.drawString(100, y, f"User: {prediction.user.username}")
            y -= 40

            # Price data
            p.setFont("Helvetica-Bold", 14)
            p.drawString(100, y, "Price Data:")
            y -= 25
            p.setFont("Helvetica", 12)

            p.drawString(120, y, f"Open: ${prediction.open_price}")
            y -= 15
            p.drawString(120, y, f"High: ${prediction.high_price}")
            y -= 15
            p.drawString(120, y, f"Low: ${prediction.low_price}")
            y -= 15
            p.drawString(120, y, f"Close: ${prediction.close_price}")
            y -= 15
            p.drawString(120, y, f"Volume: {prediction.volume:,}")
            y -= 40

            # Prediction result
            p.setFont("Helvetica-Bold", 14)
            p.drawString(100, y, "Prediction Result:")
            y -= 25
            p.setFont("Helvetica", 12)

            p.drawString(120, y, f"Predicted Price: ${prediction.predicted_price}")
            y -= 15
            p.drawString(120, y, f"Recommendation: {prediction.recommendation}")
            y -= 40

            p.showPage()
            p.save()

            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="prediction_report_{prediction_id}.pdf"'

            return response

        except PredictionHistory.DoesNotExist:
            return Response({'error': 'Prediction not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {'error': 'Failed to generate PDF', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckAPIView(APIView):
    """API health check"""

    permission_classes = [AllowAny]

    def get(self, request):
        # check AI predictor module for model presence
        try:
            from ai import predictor
            predictor._load_model()
            model_status = predictor._model is not None
        except Exception:
            model_status = False

        return Response(
            {
                'status': 'healthy',
                'message': 'TradeIQ API is running',
                'model_loaded': model_status,
                'timestamp': datetime.now().isoformat()
            },
            status=status.HTTP_200_OK
        )


class AdminDashboardAPIView(APIView):
    """Dashboard stats for staff (Admin, Researcher, Analyst)"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.userprofile
            if profile.role not in ['admin', 'researcher', 'analyst']:
                return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)

        # User stats
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        blocked_users = total_users - active_users

        # Role breakdown
        role_counts = {}
        for role_choice in ['admin', 'investor', 'analyst', 'researcher']:
            role_counts[role_choice] = UserProfile.objects.filter(role=role_choice).count()

        # Prediction stats
        total_predictions = PredictionHistory.objects.count()
        today = timezone.localdate()
        start_day = today - timedelta(days=6)
        prediction_counts = (
            PredictionHistory.objects.filter(created_at__date__gte=start_day)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        prediction_count_lookup = {
            item['day'].date() if hasattr(item['day'], 'date') else item['day']: item['count']
            for item in prediction_counts
        }
        prediction_trend = []
        for offset in range(7):
            day = start_day + timedelta(days=offset)
            prediction_trend.append({
                'date': day.strftime('%d %b'),
                'iso_date': day.isoformat(),
                'count': prediction_count_lookup.get(day, 0),
            })

        top_operator_rows = (
            PredictionHistory.objects.values('user__username', 'user__userprofile__role')
            .annotate(count=Count('id'))
            .order_by('-count', 'user__username')[:5]
        )
        top_operators = [
            {
                'username': row['user__username'] or 'Unknown',
                'role': row['user__userprofile__role'] or 'investor',
                'count': row['count'],
            }
            for row in top_operator_rows
        ]

        recent_activity_count = ActivityLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(days=1)
        ).count()
        active_model = _ensure_active_model_history()
        
        # Recent activity logs (last 10)
        recent_logs = ActivityLog.objects.select_related('user').order_by('-timestamp')[:10]
        recent_activity = [
            {
                'user': log.user.username,
                'action': log.action,
                'role': log.role,
                'timestamp': log.timestamp.isoformat()
            }
            for log in recent_logs
        ]

        return Response({
            'users': {
                'total': total_users,
                'active': active_users,
                'blocked': blocked_users,
                'by_role': role_counts
            },
            'predictions': {
                'total': total_predictions,
            },
            'system': {
                'api_status': 'online',
                'timestamp': datetime.now().isoformat(),
                'recent_activity_count': recent_activity_count,
                'active_model': active_model.name if active_model else None,
            },
            'prediction_trend': prediction_trend,
            'top_operators': top_operators,
            'recent_activity': recent_activity
        })


class AdminStockFetchAPIView(APIView):
    """Staff endpoint to fetch live stock data"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.userprofile
            if profile.role not in ['admin', 'researcher']:
                return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)

        symbol = request.query_params.get('symbol', 'AAPL').upper()
        
        try:
            resolved_symbol, hist = resolve_symbol_with_history(symbol, period='1mo')

            if hist is None or hist.empty:
                return Response({'error': f'No data found for: {symbol}'}, status=404)

            rows = []
            for date, row in hist.iterrows():
                rows.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': round(float(row['Open']), 2),
                    'high': round(float(row['High']), 2),
                    'low': round(float(row['Low']), 2),
                    'close': round(float(row['Close']), 2),
                    'volume': int(row['Volume']),
                })

            return Response({
                'symbol': resolved_symbol,
                'row_count': len(rows),
                'data': rows
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)
