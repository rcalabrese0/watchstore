from django.utils import timezone
from store.models import Customer, Product, Order, OrderItem
from decimal import Decimal
import random

def create_sample_orders():
    # Crear un cliente de prueba si no existe
    customer, created = Customer.objects.get_or_create(
        email='cliente@ejemplo.com',
        defaults={
            'username': 'cliente@ejemplo.com',
            'dni': '12345678',
            'phone': '555-1234',
            'address': 'Calle Ejemplo 123'
        }
    )
    if created:
        customer.set_password('12345678')
        customer.save()
        print(f"Cliente creado: {customer.email}")

    # Obtener todos los productos
    products = list(Product.objects.filter(active=True))
    
    if not products:
        print("No hay productos disponibles")
        return

    # Crear algunos pedidos de ejemplo
    for i in range(3):
        # Crear un pedido
        order = Order.objects.create(
            customer=customer,
            status=random.choice(['pending', 'in_process', 'completed'])
        )
        
        # Agregar items aleatorios al pedido
        num_items = random.randint(1, 3)
        total = Decimal('0')
        
        for _ in range(num_items):
            product = random.choice(products)
            quantity = random.randint(1, 2)
            price = product.price
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )
            
            total += price * quantity
        
        order.total = total
        order.save()
        
        print(f"Pedido #{order.id} creado - Total: ${order.total}")

if __name__ == '__main__':
    import django
    django.setup()
    create_sample_orders()
