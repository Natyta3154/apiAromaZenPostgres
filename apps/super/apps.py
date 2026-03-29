from django.apps import AppConfig
from django.contrib.auth import get_user_model
from decouple import config
import os

class SuperConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.super"

    def ready(self):
        # Evitamos que se ejecute dos veces en el servidor de desarrollo
        if os.environ.get('RUN_MAIN') == 'true':
            return

        try:
            User = get_user_model()
            
            # Usamos 'config' de decouple para ser consistente con tu settings.py
            username = config("DJANGO_SUPERUSER_USERNAME", default=None)
            email = config("DJANGO_SUPERUSER_EMAIL", default=None)
            password = config("DJANGO_SUPERUSER_PASSWORD", default=None)

            if username and password:
                if not User.objects.filter(username=username).exists():
                    print(f"--- Creando superusuario: {username} ---")
                    User.objects.create_superuser(
                        username=username, 
                        email=email, 
                        password=password
                    )
                    print("✅ Superusuario creado con éxito.")
                else:
                    print(f"ℹ️ El superusuario '{username}' ya existe.")
        except Exception as e:
            # Es importante atrapar errores aquí para que no rompa el inicio de la app
            print(f"⚠️ Error al intentar crear el superusuario: {e}")
