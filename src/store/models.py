from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Customer(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('seller', 'Vendedor'),
        ('customer', 'Cliente'),
    ]
    
    username = None  # Deshabilitamos el campo username
    email = models.EmailField(unique=True)
    dni = models.CharField(max_length=20, unique=True, verbose_name='DNI')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono')
    address = models.TextField(blank=True, null=True, verbose_name='Dirección')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer', verbose_name='Rol')
    has_discount = models.BooleanField(default=False, verbose_name='Tiene descuento')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['dni']

    class Meta:
        db_table = 'customer'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.email

class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='categories')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.parent:
            return f"{self.brand.name} - {self.parent.name} - {self.name}"
        return f"{self.brand.name} - {self.name}"
    
    class Meta:
        verbose_name_plural = "categories"
        ordering = ['brand', 'parent__name', 'name']
        unique_together = [['brand', 'parent', 'name']]

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    display_order = models.IntegerField(default=0, help_text="Orden de visualización del producto (menor número aparece primero)")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['display_order', 'name']

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'En Proceso'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observations = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    shipping_method = models.CharField(max_length=100, verbose_name='Medio de transporte', default='Retiro en tienda')
    target_customer = models.CharField(max_length=255, blank=True, null=True, verbose_name='Cliente')

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']

    def __str__(self):
        return f"Pedido #{self.id} - {self.customer.email}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)
