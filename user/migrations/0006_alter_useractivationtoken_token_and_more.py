# Generated by Django 5.0 on 2023-12-25 05:19

import django.db.models.deletion
import user.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_alter_user_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useractivationtoken',
            name='token',
            field=models.CharField(default=user.models.get_token, max_length=50),
        ),
        migrations.AlterField(
            model_name='useractivationtoken',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
