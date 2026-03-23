"""
Django models for TradeIQ prediction system
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class UserProfile(models.Model):
    """
    Extended user profile with role information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=[
            ('admin', 'Admin'),
            ('investor', 'Investor'),
            ('analyst', 'Market Analyst'),
            ('researcher', 'Researcher'),
        ],
        default='investor'
    )

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Dataset(models.Model):
    """
    Uploaded datasets for model training
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='datasets/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    row_count = models.PositiveIntegerField(default=0)
    column_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'datasets'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.name


class ModelHistory(models.Model):
    """
    History of trained models with performance metrics
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    model_file = models.FileField(upload_to='models/')
    rmse = models.FloatField()
    r_squared = models.FloatField()
    training_date = models.DateTimeField(auto_now_add=True)
    dataset_used = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = 'model_history'
        ordering = ['-training_date']

    def __str__(self):
        return f"{self.name} (RMSE: {self.rmse:.4f}, R²: {self.r_squared:.4f})"


class PredictionHistory(models.Model):
    """
    History of all predictions made by users
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock_symbol = models.CharField(max_length=20)

    # Input features
    open_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    high_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    low_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    close_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    volume = models.BigIntegerField(validators=[MinValueValidator(0)])

    # Moving averages
    ma_5 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ma_10 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ma_20 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Daily return
    daily_return = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    # Prediction results
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    recommendation = models.CharField(max_length=4, choices=[
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        ('HOLD', 'Hold')
    ])

    # Model performance
    rmse = models.FloatField(null=True, blank=True)
    r_squared = models.FloatField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    model_used = models.ForeignKey(ModelHistory, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'prediction_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['stock_symbol', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.stock_symbol} - {self.recommendation} ({self.created_at.date()})"


class Portfolio(models.Model):
    """
    Simple portfolio entry to track user holdings.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock_symbol = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    average_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'portfolio'
        ordering = ['-added_at']
        indexes = [models.Index(fields=['user', 'stock_symbol'])]

    def __str__(self):
        return f"{self.user.username} - {self.stock_symbol} x{self.quantity} @ {self.average_price}"


class ActivityLog(models.Model):
    """
    Activity logs for auditing user actions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('investor', 'Investor'),
        ('analyst', 'Market Analyst'),
        ('researcher', 'Researcher'),
    ])
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'activity_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.action} ({self.timestamp})"


# Signal to create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)