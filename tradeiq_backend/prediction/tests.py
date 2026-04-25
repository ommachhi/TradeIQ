from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from prediction.models import ActivityLog, ModelHistory, PredictionHistory
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


User = get_user_model()


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)
class AuthenticationSecurityTests(APITestCase):
    def test_registration_hashes_password_with_bcrypt(self):
        response = self.client.post(
            '/api/auth/register/',
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'SecurePass123',
                'password_confirm': 'SecurePass123',
                'role': 'investor',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='newuser')
        self.assertTrue(user.password.startswith('bcrypt_sha256$'))

    def test_registration_rejects_duplicate_email_case_insensitive(self):
        User.objects.create_user(
            username='existing-user',
            email='duplicate@example.com',
            password='SecurePass123',
        )

        response = self.client.post(
            '/api/auth/register/',
            {
                'username': 'another-user',
                'email': 'DUPLICATE@example.com',
                'password': 'SecurePass123',
                'password_confirm': 'SecurePass123',
                'role': 'investor',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_registration_rejects_duplicate_username_case_insensitive(self):
        User.objects.create_user(
            username='ExistingUser',
            email='existing@example.com',
            password='SecurePass123',
        )

        response = self.client.post(
            '/api/auth/register/',
            {
                'username': 'existinguser',
                'email': 'different@example.com',
                'password': 'SecurePass123',
                'password_confirm': 'SecurePass123',
                'role': 'investor',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_login_accepts_email_identifier(self):
        User.objects.create_user(
            username='email-login-user',
            email='emaillogin@example.com',
            password='SecurePass123',
        )

        response = self.client.post(
            '/api/auth/login/',
            {
                'username': 'emaillogin@example.com',
                'password': 'SecurePass123',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'email-login-user')

    def test_blocked_user_cannot_log_in(self):
        blocked_user = User.objects.create_user(
            username='blocked-user',
            email='blocked@example.com',
            password='SecurePass123',
            is_active=False,
        )

        response = self.client.post(
            '/api/auth/login/',
            {
                'username': blocked_user.username,
                'password': 'SecurePass123',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'This account has been blocked by admin')


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)
class AdminUserManagementTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin-user',
            email='admin@example.com',
            password='SecurePass123',
        )
        self.admin_user.userprofile.role = 'admin'
        self.admin_user.userprofile.save(update_fields=['role'])
        self.client.force_authenticate(user=self.admin_user)

    def test_admin_can_delete_user(self):
        target_user = User.objects.create_user(
            username='delete-me',
            email='delete-me@example.com',
            password='SecurePass123',
        )

        response = self.client.delete(f'/api/admin/users/{target_user.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=target_user.pk).exists())

    def test_admin_user_list_excludes_last_seen_field(self):
        User.objects.create_user(
            username='listed-user',
            email='listed@example.com',
            password='SecurePass123',
        )

        response = self.client.get('/api/admin/users/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)
        self.assertNotIn('last_login', response.data[0])

    def test_dashboard_stats_include_trend_and_top_operators(self):
        operator = User.objects.create_user(
            username='operator-user',
            email='operator@example.com',
            password='SecurePass123',
        )

        PredictionHistory.objects.create(
            user=operator,
            stock_symbol='AAPL',
            open_price=100,
            high_price=105,
            low_price=99,
            close_price=102,
            volume=100000,
            predicted_price=103,
            recommendation='BUY',
        )
        ActivityLog.objects.create(
            user=self.admin_user,
            action='Viewed dashboard',
            role='admin',
        )

        response = self.client.get('/api/admin/dashboard/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('prediction_trend', response.data)
        self.assertEqual(len(response.data['prediction_trend']), 7)
        self.assertIn('top_operators', response.data)
        self.assertEqual(response.data['top_operators'][0]['username'], 'operator-user')

    def test_dashboard_marks_latest_model_active_when_none_is_flagged(self):
        legacy_model = ModelHistory.objects.create(
            name='LegacyModel',
            model_file='models/legacy-model.pkl',
            rmse=1.25,
            r_squared=0.42,
            is_active=False,
        )

        response = self.client.get('/api/admin/dashboard/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['system']['active_model'], 'LegacyModel')
        legacy_model.refresh_from_db()
        self.assertTrue(legacy_model.is_active)


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)
class ResearchPanelTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='research-user',
            email='research@example.com',
            password='SecurePass123',
        )
        self.client.force_authenticate(user=self.user)

    @patch('prediction.views.build_research_panel')
    def test_research_panel_returns_unified_payload(self, mock_build_research_panel):
        mock_build_research_panel.return_value = {
            'symbol': 'RELIANCE.NS',
            'company_name': 'Reliance Industries',
            'selected_range': '1m',
            'range_label': '1M',
            'overview': {
                'company_name': 'Reliance Industries',
                'symbol': 'RELIANCE.NS',
                'currency': 'INR',
                'current_price': 2885.3,
                'price_change': 24.5,
                'price_change_pct': 0.86,
                'market_cap': 19500000000000,
                'volume': 1234567,
                'fifty_two_week_high': 3025.0,
                'fifty_two_week_low': 2220.0,
                'as_of': '2026-04-02T10:00:00Z',
            },
            'chart': {
                'range': '1m',
                'points': [
                    {'label': '01 Apr', 'timestamp': '2026-04-01T00:00:00Z', 'open': 2850.0, 'high': 2890.0, 'low': 2840.0, 'close': 2885.3, 'volume': 1234567},
                ],
            },
            'technical_analysis': {
                'moving_averages': {'ma_20': 2821.0, 'ma_50': 2760.0, 'ema_20': 2833.0, 'ema_50': 2772.0},
                'rsi': 59.4,
                'macd': {'macd': 12.2, 'signal': 8.4, 'histogram': 3.8},
                'support': 2790.0,
                'resistance': 2910.0,
                'trend': 'Uptrend',
                'volatility_pct': 21.5,
            },
            'ai_prediction': {
                'predicted_price': 2920.0,
                'direction': 'Up',
                'confidence_pct': 68,
                'confidence_label': 'Medium',
                'risk_score': 42,
                'risk_level': 'Medium',
                'change_percent': 1.2,
                'recommendation': 'BUY',
                'warning': '',
            },
            'news_sentiment': {
                'items': [
                    {'headline': 'Reliance expands digital business', 'source': 'Reuters', 'url': 'https://example.com', 'published_at': '2026-04-02T08:00:00Z', 'sentiment': 'Positive', 'sentiment_score': 1},
                ],
                'summary': {'overall': 'Positive', 'positive': 1, 'negative': 0, 'neutral': 0, 'summary': 'Positive feed overall.'},
            },
            'recommendation': {'action': 'BUY', 'score': 3, 'reason': 'Momentum and sentiment both support upside.'},
        }

        response = self.client.get('/api/research/?symbol=RELIANCE.NS&range=1m')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['overview']['symbol'], 'RELIANCE.NS')
        self.assertIn('technical_analysis', response.data['data'])
        self.assertIn('news_sentiment', response.data['data'])
        self.assertEqual(response.data['data']['recommendation']['action'], 'BUY')
