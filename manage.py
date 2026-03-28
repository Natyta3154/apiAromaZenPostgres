#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """
    Función principal para ejecutar tareas administrativas de Django.
    Aquí se establece la configuración del proyecto y se pasan los comandos
    recibidos por la terminal al núcleo de Django.
    """
    # Establece el módulo de configuración por defecto para 'manage.py'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        # Importa la función que ejecuta comandos desde la línea de comandos
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Si Django no está instalado o el entorno virtual no está activo, lanza este error detallado
        raise ImportError(
            "No se pudo importar Django. ¿Estás seguro de que está instalado y "
            "disponible en tu variable de entorno PYTHONPATH? ¿Olvidaste activar "
            "tu entorno virtual?"
        ) from exc
    
    # Pasa los argumentos de la terminal (como 'runserver', 'migrate', etc.) a Django
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
