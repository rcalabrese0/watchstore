# Generated by Django 5.0.2 on 2025-04-10 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_customer_has_discount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='username',
        ),
        migrations.AlterField(
            model_name='customer',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
