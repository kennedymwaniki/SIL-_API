# Generated by Django 5.1.7 on 2025-03-27 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='order_code',
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
    ]
