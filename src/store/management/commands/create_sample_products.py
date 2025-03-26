import os
from django.core.management.base import BaseCommand
from django.core.files import File
from store.models import Product, Brand, Category
from django.conf import settings
from decimal import Decimal

class Command(BaseCommand):
    help = 'Crea productos de ejemplo con imágenes'

    def handle(self, *args, **kwargs):
        products_data = [
            {
                'name': 'Casio G-Shock DW5600',
                'brand_name': 'Casio',
                'category_name': 'G-Shock',
                'description': 'Reloj digital resistente a golpes con diseño clásico',
                'price': Decimal('89.99'),
                'stock': 15,
                'sku': 'CAS-GS-001',
                'image_name': 'gshock.jpg'
            },
            {
                'name': 'X-Time Runner Pro',
                'brand_name': 'X-Time',
                'category_name': 'Runner',
                'description': 'Reloj deportivo con cronómetro y monitor de ritmo cardíaco',
                'price': Decimal('59.99'),
                'stock': 20,
                'sku': 'XT-RUN-001',
                'image_name': 'runner.jpg'
            },
            {
                'name': 'Lemon Pop Color',
                'brand_name': 'Lemon',
                'category_name': 'Pop',
                'description': 'Reloj juvenil con diseño colorido y correa intercambiable',
                'price': Decimal('29.99'),
                'stock': 25,
                'sku': 'LEM-POP-001',
                'image_name': 'pop.jpg'
            },
            {
                'name': 'Casio Edifice EF-539',
                'brand_name': 'Casio',
                'category_name': 'Edifice',
                'description': 'Reloj analógico deportivo con cronógrafo',
                'price': Decimal('149.99'),
                'stock': 10,
                'sku': 'CAS-ED-001',
                'image_name': 'edifice.jpg'
            }
        ]

        # Asegurarse de que el directorio de imágenes existe
        sample_images_dir = os.path.join(settings.BASE_DIR, 'store', 'sample_images')
        if not os.path.exists(sample_images_dir):
            os.makedirs(sample_images_dir)

        for product_data in products_data:
            try:
                brand = Brand.objects.get(name=product_data['brand_name'])
                category = Category.objects.get(
                    name=product_data['category_name'],
                    brand=brand
                )

                # Verificar si el producto ya existe
                if not Product.objects.filter(sku=product_data['sku']).exists():
                    product = Product(
                        name=product_data['name'],
                        brand=brand,
                        category=category,
                        description=product_data['description'],
                        price=product_data['price'],
                        stock=product_data['stock'],
                        sku=product_data['sku']
                    )

                    # Cargar imagen desde el directorio de imágenes de ejemplo
                    image_path = os.path.join(sample_images_dir, product_data['image_name'])
                    if os.path.exists(image_path):
                        with open(image_path, 'rb') as img_file:
                            product.image.save(
                                product_data['image_name'],
                                File(img_file),
                                save=True
                            )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Imagen no encontrada: {product_data["image_name"]}'
                            )
                        )

                    product.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Producto creado exitosamente: {product.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'El producto {product_data["name"]} ya existe')
                    )

            except Brand.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'La marca {product_data["brand_name"]} no existe')
                )
            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f'La categoría {product_data["category_name"]} '
                        f'no existe para la marca {product_data["brand_name"]}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creando producto {product_data["name"]}: {str(e)}')
                )
