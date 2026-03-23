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
from django.db.models import Count, Avg
from django.utils import timezone
from pathlib import Path
import pandas as pd
import yfinance as yf
import os
import uuid
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

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
    PDFReportSerializer
)
from .models import Dataset, ModelHistory, PredictionHistory, ActivityLog, UserProfile, Portfolio
# Import ml_model only when needed to avoid startup issues
# from .ml_model import StockPricePredictor, stock_predictor

User = get_user_model()


def _get_user_role(user, default='investor'):
    try:
        return user.userprofile.role
    except UserProfile.DoesNotExist:
        return default


# Authentication Views
class RegisterView(APIView):
    """User registration endpoint"""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            # Log activity
            try:
                profile = user.userprofile
                ActivityLog.objects.create(
                    user=user,
                    action="User registered",
                    role=profile.role
                )
            except UserProfile.DoesNotExist:
                ActivityLog.objects.create(
                    user=user,
                    action="User registered",
                    role='investor'
                )

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
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)

            # Log activity
            try:
                profile = user.userprofile
                ActivityLog.objects.create(
                    user=user,
                    action="User logged in",
                    role=profile.role
                )
            except UserProfile.DoesNotExist:
                ActivityLog.objects.create(
                    user=user,
                    action="User logged in",
                    role='investor'
                )

            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })

        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


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
                return Response(
                    {'error': 'Invalid input data', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            validated_data = serializer.validated_data

            # run prediction
            result = self._run_prediction(validated_data, request.user)
            return Response(result)

        except Exception as e:
            return Response({'error': 'Prediction failed', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        # allow GET /api/predict/?symbol=AAPL for convenience
        symbol = request.query_params.get('symbol')
        if not symbol:
            return Response({'error': 'Symbol query parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        validated = {'symbol': symbol}
        serializer = PredictionSerializer(data=validated)
        if not serializer.is_valid():
            return Response({'error': 'Invalid input data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self._run_prediction(serializer.validated_data, request.user))


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
                return Response(
                    {'error': 'Invalid symbol'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Fetch data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)

            if hist.empty:
                return Response(
                    {'error': f'No data found for symbol: {symbol}'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Format data for charts
            data = []
            for date, row in hist.iterrows():
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'close': round(float(row['Close']), 2)
                })

            return Response({
                'symbol': symbol,
                'period': period,
                'data': data
            })

        except Exception as e:
            return Response(
                {'error': 'Failed to fetch stock data', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Stock lookup endpoint

class StockAPIView(APIView):
    """Return recent OHLCV data for a symbol"""

    permission_classes = [AllowAny]

    def get(self, request):
        serializer = StockDataSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        symbol = serializer.validated_data['symbol']
        period = serializer.validated_data.get('period', '1d')
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            if hist.empty:
                return Response({'error': 'No data found for symbol'}, status=status.HTTP_404_NOT_FOUND)
            data = []
            for date, row in hist.iterrows():
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume']),
                })
            return Response({'symbol': symbol, 'period': period, 'data': data})
        except Exception as e:
            return Response({'error': 'Failed to fetch stock data', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

        users = User.objects.all()
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
            serializer = UserManagementSerializer(user, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()

                # Update role in profile if provided
                if 'role' in request.data:
                    try:
                        user_profile = user.userprofile
                        user_profile.role = request.data['role']
                        user_profile.save()
                    except UserProfile.DoesNotExist:
                        UserProfile.objects.create(user=user, role=request.data['role'])

                # Log activity
                ActivityLog.objects.create(
                    user=request.user,
                    action=f"Updated user {user.username}",
                    role=request.user.userprofile.role
                )

                return Response(serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


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

            # Save model history
            model_history = ModelHistory.objects.create(
                name=training_result['model_name'],
                model_file=training_result['model_path'],
                rmse=training_result['test_rmse'],
                r_squared=training_result['test_r2'],
                dataset_used=dataset if dataset_id else None
            )

            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action=f"Retrained model {model_name}",
                role=_get_user_role(request.user)
            )

            return Response({
                'message': 'Model retrained successfully',
                'model': ModelHistorySerializer(model_history).data,
                'metrics': {
                    'rmse': training_result['test_rmse'],
                    'r_squared': training_result['test_r2']
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

        models = ModelHistory.objects.all().order_by('-training_date')
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
                'timestamp': datetime.now().isoformat()
            },
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
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1mo')

            if hist.empty:
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
                'symbol': symbol,
                'row_count': len(rows),
                'data': rows
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)
