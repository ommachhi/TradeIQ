from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prediction', '0004_auth_user_case_insensitive_uniques'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelhistory',
            name='feature_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='modelhistory',
            name='overfit_gap',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='modelhistory',
            name='testing_samples',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='modelhistory',
            name='train_r_squared',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='modelhistory',
            name='train_rmse',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='modelhistory',
            name='training_samples',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
