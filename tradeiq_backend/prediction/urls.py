"""
URL routing for prediction app
"""

from django.urls import path
from .views import (
    # Authentication
    RegisterView,
    LoginView,
    ProfileView,

    # Predictions
    PredictionAPIView,
    StockHistoryAPIView,
    StockAPIView,
    ResearchPanelAPIView,

    # Admin
    UserManagementAPIView,
    PortfolioAPIView,
    DatasetManagementAPIView,
    ModelRetrainingAPIView,
    ModelHistoryAPIView,
    PredictionHistoryAPIView,
    ActivityLogAPIView,
    AdminDashboardAPIView,
    AdminStockFetchAPIView,

    # Reports
    PDFReportAPIView,

    # Legacy
    HealthCheckAPIView
)

app_name = 'prediction'

urlpatterns = [
    # Authentication
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),

    # Predictions
    path('predict/', PredictionAPIView.as_view(), name='predict'),
    path('stock-history/', StockHistoryAPIView.as_view(), name='stock_history'),
    path('stock/', StockAPIView.as_view(), name='stock'),
    path('research/', ResearchPanelAPIView.as_view(), name='research'),

    # Admin
    path('admin/users/', UserManagementAPIView.as_view(), name='user_management'),
    path('admin/users/<int:pk>/', UserManagementAPIView.as_view(), name='user_detail'),
    path('admin/datasets/', DatasetManagementAPIView.as_view(), name='dataset_management'),
    path('admin/retrain/', ModelRetrainingAPIView.as_view(), name='model_retrain'),
    path('admin/models/', ModelHistoryAPIView.as_view(), name='model_history'),
    path('admin/predictions/', PredictionHistoryAPIView.as_view(), name='prediction_history'),
    path('admin/logs/', ActivityLogAPIView.as_view(), name='activity_logs'),
    path('admin/dashboard/', AdminDashboardAPIView.as_view(), name='admin_dashboard'),
    path('admin/stock-fetch/', AdminStockFetchAPIView.as_view(), name='admin_stock_fetch'),

    # Reports
    path('reports/pdf/', PDFReportAPIView.as_view(), name='pdf_report'),

    # Portfolio endpoints
    path('portfolio/add/', PortfolioAPIView.as_view(), name='portfolio_add'),
    path('portfolio/', PortfolioAPIView.as_view(), name='portfolio'),

    # Legacy/compat endpoints
    path('health/', HealthCheckAPIView.as_view(), name='health'),
]
