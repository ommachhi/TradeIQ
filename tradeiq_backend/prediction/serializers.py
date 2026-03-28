"""
Django Serializers for REST API

Serializers handle validation and conversion between Python objects and JSON
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Dataset, ModelHistory, PredictionHistory, ActivityLog, UserProfile, Portfolio
from .symbols import resolve_symbol_with_history, is_valid_stock_symbol_format

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    role = serializers.CharField(source='userprofile.role', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[
        ('admin', 'Admin'),
        ('investor', 'Investor'),
        ('analyst', 'Market Analyst'),
        ('researcher', 'Researcher'),
    ], default='investor')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'role']

    def validate(self, data):
        # password_confirm may be omitted by legacy clients
        pwd = data.get('password')
        confirm = data.get('password_confirm')
        if confirm is None:
            return data
        if pwd != confirm:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        role = validated_data.pop('role')
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)

        # The post_save signal creates the profile automatically.
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.save()

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""

    class Meta:
        model = UserProfile
        fields = ['role']

    def update(self, instance, validated_data):
        instance.role = validated_data.get('role', instance.role)
        instance.save()
        return instance


class PredictionSerializer(serializers.Serializer):
    """
    Serializer for stock price prediction input

    Now supports both manual input and stock symbol based prediction
    """
    # Optional stock symbol
    symbol = serializers.CharField(required=False, max_length=20)

    # Manual input fields (required if symbol not provided)
    open = serializers.FloatField(required=False, min_value=0)
    high = serializers.FloatField(required=False, min_value=0)
    low = serializers.FloatField(required=False, min_value=0)
    volume = serializers.IntegerField(required=False, min_value=0)

    def validate(self, data):
        """
        Validation logic:
        - Either symbol OR all manual fields must be provided
        - If manual fields provided, validate logical constraints
        """
        symbol = data.get('symbol')
        manual_fields = ['open', 'high', 'low', 'volume']

        if symbol:
            symbol = symbol.strip().upper()
            if not is_valid_stock_symbol_format(symbol):
                raise serializers.ValidationError(
                    "Invalid stock symbol. Please enter a valid symbol like AAPL, RELIANCE.NS, TCS.NS"
                )

            # Symbol provided - fetch data from Yahoo Finance
            try:
                resolved_symbol, hist = resolve_symbol_with_history(symbol, period="2y")

                if hist is None or hist.empty:
                    raise serializers.ValidationError(
                        "Invalid stock symbol. Please enter a valid symbol like AAPL, RELIANCE.NS, TCS.NS"
                    )

                data['symbol'] = resolved_symbol

                # Get latest data
                latest = hist.iloc[-1]
                data['open'] = float(latest['Open'])
                data['high'] = float(latest['High'])
                data['low'] = float(latest['Low'])
                data['volume'] = int(latest['Volume'])
                data['close'] = float(latest['Close'])

                # Calculate additional features
                data.update(self._calculate_features(hist))

            except TimeoutError:
                raise serializers.ValidationError(
                    "Symbol lookup timed out. Please try again with a valid symbol like AAPL, RELIANCE.NS, TCS.NS"
                )
            except serializers.ValidationError:
                raise
            except Exception:
                raise serializers.ValidationError(
                    "Invalid stock symbol. Please enter a valid symbol like AAPL, RELIANCE.NS, TCS.NS"
                )
        else:
            # Manual input - validate all fields present
            missing_fields = [field for field in manual_fields if field not in data]
            if missing_fields:
                raise serializers.ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

            # Validate logical constraints
            if data['high'] < data['low']:
                raise serializers.ValidationError("High price must be greater than or equal to low price")

            if data['open'] < data['low'] or data['open'] > data['high']:
                raise serializers.ValidationError("Open price must be between low and high prices")

        return data

    def _calculate_features(self, hist):
        """Calculate technical indicators"""
        features = {}

        # Moving averages
        features['ma_5'] = hist['Close'].rolling(window=5).mean().iloc[-1] if len(hist) >= 5 else hist['Close'].iloc[-1]
        features['ma_10'] = hist['Close'].rolling(window=10).mean().iloc[-1] if len(hist) >= 10 else hist['Close'].iloc[-1]
        features['ma_20'] = hist['Close'].rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else hist['Close'].iloc[-1]

        # Daily return
        if len(hist) >= 2:
            features['daily_return'] = (hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]
        else:
            features['daily_return'] = 0.0

        return features


class PredictionResponseSerializer(serializers.Serializer):
    """
    Serializer for prediction response
    """
    symbol = serializers.CharField(required=False)
    predicted_price = serializers.FloatField()
    recommendation = serializers.CharField()
    confidence = serializers.FloatField(required=False)
    input_features = serializers.DictField()
    technical_indicators = serializers.DictField(required=False)
    rmse = serializers.FloatField(required=False)
    r_squared = serializers.FloatField(required=False)


class HistoryDataSerializer(serializers.Serializer):
    """
    Serializer for historical stock data
    """
    date = serializers.DateField()
    open = serializers.FloatField()
    high = serializers.FloatField()
    low = serializers.FloatField()
    close = serializers.FloatField()
    volume = serializers.IntegerField()


class StockHistorySerializer(serializers.Serializer):
    """
    Serializer for stock history API
    """
    symbol = serializers.CharField(max_length=20)
    period = serializers.CharField(default='1y', max_length=10)

    def validate_period(self, value):
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        if value not in valid_periods:
            raise serializers.ValidationError(f"Invalid period. Must be one of: {', '.join(valid_periods)}")
        return value


class DatasetSerializer(serializers.ModelSerializer):
    """Serializer for Dataset model"""

    class Meta:
        model = Dataset
        fields = ['id', 'name', 'file', 'uploaded_by', 'uploaded_at', 'row_count', 'column_count']
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at', 'row_count', 'column_count']


class ModelHistorySerializer(serializers.ModelSerializer):
    """Serializer for ModelHistory model"""

    dataset_name = serializers.CharField(source='dataset_used.name', read_only=True)

    class Meta:
        model = ModelHistory
        fields = ['id', 'name', 'model_file', 'rmse', 'r_squared', 'training_date', 'dataset_used', 'dataset_name', 'is_active']
        read_only_fields = ['id', 'training_date']


class PredictionHistorySerializer(serializers.ModelSerializer):
    """Serializer for PredictionHistory model"""

    username = serializers.CharField(source='user.username', read_only=True)
    user_role = serializers.CharField(source='user.userprofile.role', read_only=True)

    class Meta:
        model = PredictionHistory
        fields = [
            'id', 'user', 'username', 'user_role', 'stock_symbol',
            'open_price', 'high_price', 'low_price', 'close_price', 'volume',
            'ma_5', 'ma_10', 'ma_20', 'daily_return',
            'predicted_price', 'recommendation', 'rmse', 'r_squared',
            'created_at', 'model_used'
        ]
        read_only_fields = ['id', 'created_at']


class PortfolioSerializer(serializers.ModelSerializer):
    """Serializer for Portfolio model"""

    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Portfolio
        fields = ['id', 'user', 'username', 'stock_symbol', 'quantity', 'average_price', 'added_at']
        read_only_fields = ['id', 'user', 'username', 'added_at']


class StockDataSerializer(serializers.Serializer):
    """Serializer to validate stock query parameters"""
    symbol = serializers.CharField(max_length=20)
    period = serializers.CharField(default='1y', max_length=10)

    def validate_symbol(self, value):
        cleaned = (value or '').strip().upper()
        if not is_valid_stock_symbol_format(cleaned):
            raise serializers.ValidationError(
                "Invalid stock symbol. Please enter a valid symbol like AAPL, RELIANCE.NS, TCS.NS"
            )
        return cleaned

    def validate_period(self, value):
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        if value not in valid_periods:
            raise serializers.ValidationError(f"Invalid period. Must be one of: {', '.join(valid_periods)}")
        return value


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for ActivityLog model"""

    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'username', 'action', 'role', 'timestamp', 'ip_address', 'user_agent']
        read_only_fields = ['id', 'timestamp']


class UserManagementSerializer(serializers.ModelSerializer):
    """Serializer for admin user management"""

    role = serializers.CharField(source='userprofile.role')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']


class RetrainModelSerializer(serializers.Serializer):
    """Serializer for model retraining request"""

    dataset_id = serializers.UUIDField(required=False)
    model_name = serializers.CharField(max_length=255, default="Auto-trained Model")


class PDFReportSerializer(serializers.Serializer):
    """Serializer for PDF report generation"""

    prediction_id = serializers.UUIDField()
    include_charts = serializers.BooleanField(default=True)
