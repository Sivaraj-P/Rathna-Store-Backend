# Generated by Django 5.0 on 2024-03-29 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_order_no_of_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]
