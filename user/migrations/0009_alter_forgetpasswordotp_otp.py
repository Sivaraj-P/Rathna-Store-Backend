# Generated by Django 5.0 on 2024-04-23 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_forgetpasswordotp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forgetpasswordotp',
            name='otp',
            field=models.CharField(max_length=50),
        ),
    ]
