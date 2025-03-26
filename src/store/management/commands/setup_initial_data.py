from django.core.management.base import BaseCommand
from store.models import Brand, Category

class Command(BaseCommand):
    help = 'Configura las marcas y categorías iniciales'

    def handle(self, *args, **kwargs):
        # Casio
        casio, _ = Brand.objects.get_or_create(
            name='Casio',
            defaults={
                'description': 'Marca japonesa líder en relojes digitales y electrónicos',
                'active': True
            }
        )

        # Categorías de Casio
        cat_casio_digital, _ = Category.objects.get_or_create(
            name='Relojes Digitales',
            brand=casio,
            defaults={'description': 'Relojes con display digital'}
        )
        Category.objects.get_or_create(
            name='G-Shock',
            brand=casio,
            parent=cat_casio_digital,
            defaults={'description': 'Línea resistente a golpes'}
        )
        Category.objects.get_or_create(
            name='Vintage',
            brand=casio,
            parent=cat_casio_digital,
            defaults={'description': 'Diseños clásicos digitales'}
        )

        cat_casio_analogico, _ = Category.objects.get_or_create(
            name='Relojes Analógicos',
            brand=casio,
            defaults={'description': 'Relojes tradicionales con agujas'}
        )
        Category.objects.get_or_create(
            name='Edifice',
            brand=casio,
            parent=cat_casio_analogico,
            defaults={'description': 'Línea deportiva elegante'}
        )

        # X-Time
        xtime, _ = Brand.objects.get_or_create(
            name='X-Time',
            defaults={
                'description': 'Relojes modernos y accesibles',
                'active': True
            }
        )

        # Categorías de X-Time
        cat_xtime_casual, _ = Category.objects.get_or_create(
            name='Casual',
            brand=xtime,
            defaults={'description': 'Relojes para uso diario'}
        )
        Category.objects.get_or_create(
            name='Urban',
            brand=xtime,
            parent=cat_xtime_casual,
            defaults={'description': 'Diseños urbanos y modernos'}
        )
        Category.objects.get_or_create(
            name='Classic',
            brand=xtime,
            parent=cat_xtime_casual,
            defaults={'description': 'Diseños tradicionales'}
        )

        cat_xtime_deportivo, _ = Category.objects.get_or_create(
            name='Deportivo',
            brand=xtime,
            defaults={'description': 'Relojes para actividades deportivas'}
        )
        Category.objects.get_or_create(
            name='Runner',
            brand=xtime,
            parent=cat_xtime_deportivo,
            defaults={'description': 'Especiales para running'}
        )

        # Lemon
        lemon, _ = Brand.objects.get_or_create(
            name='Lemon',
            defaults={
                'description': 'Relojes juveniles y coloridos',
                'active': True
            }
        )

        # Categorías de Lemon
        cat_lemon_teen, _ = Category.objects.get_or_create(
            name='Teen',
            brand=lemon,
            defaults={'description': 'Colección juvenil'}
        )
        Category.objects.get_or_create(
            name='Pop',
            brand=lemon,
            parent=cat_lemon_teen,
            defaults={'description': 'Diseños pop y coloridos'}
        )
        Category.objects.get_or_create(
            name='School',
            brand=lemon,
            parent=cat_lemon_teen,
            defaults={'description': 'Ideales para estudiantes'}
        )

        cat_lemon_kids, _ = Category.objects.get_or_create(
            name='Kids',
            brand=lemon,
            defaults={'description': 'Relojes para niños'}
        )
        Category.objects.get_or_create(
            name='Cartoon',
            brand=lemon,
            parent=cat_lemon_kids,
            defaults={'description': 'Con personajes animados'}
        )
        Category.objects.get_or_create(
            name='Learning',
            brand=lemon,
            parent=cat_lemon_kids,
            defaults={'description': 'Para aprender a leer la hora'}
        )

        self.stdout.write(self.style.SUCCESS('Marcas y categorías creadas exitosamente'))
