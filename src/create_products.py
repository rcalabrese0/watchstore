from django.core.management import BaseCommand
from store.models import Product
from decimal import Decimal

def create_sample_products():
    products = [
        {
            'name': 'Reloj Clásico Elegante',
            'description': 'Reloj analógico con correa de cuero genuino y movimiento de cuarzo japonés.',
            'price': Decimal('299.99'),
            'active': True
        },
        {
            'name': 'Smartwatch Pro',
            'description': 'Smartwatch con monitor de ritmo cardíaco, GPS y pantalla AMOLED.',
            'price': Decimal('499.99'),
            'active': True
        },
        {
            'name': 'Reloj Deportivo Resistente',
            'description': 'Reloj deportivo resistente al agua hasta 100m, cronómetro y luz LED.',
            'price': Decimal('199.99'),
            'active': True
        },
        {
            'name': 'Reloj de Lujo Automático',
            'description': 'Reloj automático con cristal de zafiro y visualización de fecha.',
            'price': Decimal('999.99'),
            'active': True
        }
    ]

    for product_data in products:
        Product.objects.get_or_create(
            name=product_data['name'],
            defaults=product_data
        )
        print(f"Producto creado/actualizado: {product_data['name']}")

if __name__ == '__main__':
    import django
    django.setup()
    create_sample_products()
