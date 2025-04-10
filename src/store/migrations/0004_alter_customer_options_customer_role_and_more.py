# Generated by Django 5.0.2 on 2025-04-10 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_product_options_product_display_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'verbose_name': 'Cliente', 'verbose_name_plural': 'Clientes'},
        ),
        migrations.AddField(
            model_name='customer',
            name='role',
            field=models.CharField(choices=[('admin', 'Administrador'), ('seller', 'Vendedor'), ('customer', 'Cliente')], default='customer', max_length=10, verbose_name='Rol'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='address',
            field=models.TextField(blank=True, null=True, verbose_name='Dirección'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='dni',
            field=models.CharField(max_length=20, unique=True, verbose_name='DNI'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Teléfono'),
        ),
    ]
