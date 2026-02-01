"""Add last_seen field to User model.

This migration was generated as a stub by the development assistant.
Run `makemigrations` and `migrate` locally if you prefer automatic generation.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_auditlog_user_agent'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_seen',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
    ]
