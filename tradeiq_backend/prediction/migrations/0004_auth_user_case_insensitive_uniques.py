from django.db import migrations


def _build_unique_username(User, original_username, pk):
    base_username = (original_username or '').strip() or f'user{pk}'
    suffix = 1
    candidate = f'{base_username}_{pk}'

    while User.objects.filter(username__iexact=candidate).exclude(pk=pk).exists():
        suffix += 1
        candidate = f'{base_username}_{pk}_{suffix}'

    return candidate


def _build_unique_email(User, original_email, pk):
    normalized = (original_email or '').strip().lower()
    if '@' in normalized:
        local_part, domain = normalized.split('@', 1)
        local_part = local_part or f'user{pk}'
        domain = domain or 'tradeiq.local'
    else:
        local_part = f'user{pk}'
        domain = 'tradeiq.local'

    suffix = 1
    candidate = f'{local_part}+dedup-{pk}@{domain}'

    while User.objects.filter(email__iexact=candidate).exclude(pk=pk).exists():
        suffix += 1
        candidate = f'{local_part}+dedup-{pk}-{suffix}@{domain}'

    return candidate


def clean_duplicate_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')

    seen_usernames = set()
    for user in User.objects.order_by('date_joined', 'id'):
        normalized_username = (user.username or '').strip().lower()
        if not normalized_username:
            user.username = _build_unique_username(User, user.username, user.pk)
            user.save(update_fields=['username'])
            normalized_username = user.username.lower()
        elif normalized_username in seen_usernames:
            user.username = _build_unique_username(User, user.username, user.pk)
            user.save(update_fields=['username'])
            normalized_username = user.username.lower()
        seen_usernames.add(normalized_username)

    seen_emails = set()
    for user in User.objects.order_by('-is_active', 'date_joined', 'id'):
        normalized_email = (user.email or '').strip().lower()
        if not normalized_email:
            continue

        if normalized_email in seen_emails:
            user.email = _build_unique_email(User, normalized_email, user.pk)
            user.save(update_fields=['email'])
            continue

        if user.email != normalized_email:
            user.email = normalized_email
            user.save(update_fields=['email'])

        seen_emails.add(normalized_email)


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('prediction', '0003_rename_prediction_portfolio_us_3dc7e9_idx_portfolio_user_id_0e9082_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(clean_duplicate_users, migrations.RunPython.noop),
        migrations.RunSQL(
            sql=(
                'CREATE UNIQUE INDEX IF NOT EXISTS prediction_auth_user_username_ci_uniq '
                'ON auth_user (LOWER(username));'
            ),
            reverse_sql='DROP INDEX IF EXISTS prediction_auth_user_username_ci_uniq;',
        ),
        migrations.RunSQL(
            sql=(
                'CREATE UNIQUE INDEX IF NOT EXISTS prediction_auth_user_email_ci_uniq '
                "ON auth_user (LOWER(email)) WHERE TRIM(email) <> '';"
            ),
            reverse_sql='DROP INDEX IF EXISTS prediction_auth_user_email_ci_uniq;',
        ),
    ]
