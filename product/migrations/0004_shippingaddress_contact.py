# Generated by Django 5.0 on 2024-01-17 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_order_orderitem_shippingaddress'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingaddress',
            name='contact',
            field=models.IntegerField(default=9089898989),
            preserve_default=False,
        ),
    ]
