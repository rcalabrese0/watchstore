from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

def create_superuser():
    User = get_user_model()
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@relojeria.com",
            password="admin123",
            dni="00000000"
        )
        print("Superusuario creado exitosamente")
    else:
        print("El superusuario ya existe")
