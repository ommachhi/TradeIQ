# Generated manually to add Portfolio model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('prediction', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('stock_symbol', models.CharField(max_length=20)),
                ('quantity', models.PositiveIntegerField()),
                ('average_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'portfolio',
                'ordering': ['-added_at'],
            },
        ),
        migrations.AddIndex(
            model_name='portfolio',
            index=models.Index(fields=['user', 'stock_symbol'], name='prediction_portfolio_us_3dc7e9_idx'),
        ),
    ]
