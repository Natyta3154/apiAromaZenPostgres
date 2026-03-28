from django.core.management.base import BaseCommand
from apps.productos.models import Categoria, Producto
from decimal import Decimal

class Command(BaseCommand):
    help = 'Puebla la base de datos con productos iniciales para el ecommerce'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando población de productos...')

        # Crear Categorías
        cat_zahumerios, _ = Categoria.objects.get_or_create(
            nombre='Zahumerios',
            defaults={'descripcion': 'Inciensos y fragancias para ambientes.'}
        )
        cat_velas, _ = Categoria.objects.get_or_create(
            nombre='Velas',
            defaults={'descripcion': 'Velas aromáticas y decorativas.'}
        )
        cat_sahumos, _ = Categoria.objects.get_or_create(
            nombre='Sahumos',
            defaults={'descripcion': 'Hierbas naturales para limpieza energética.'}
        )

        # Crear Productos para Zahumerios
        productos_zahumerios = [
            {
                'nombre': 'Zahumerio de Sándalo Real',
                'descripcion': 'Caja de 10 varillas. Ideal para meditación y relajación profunda.',
                'precio': Decimal('1250.00'),
                'stock': 100,
                'categoria': cat_zahumerios
            },
            {
                'nombre': 'Zahumerio de Lavanda Silvestre',
                'descripcion': 'Caja de 10 varillas. Fragancia suave para conciliar el sueño.',
                'precio': Decimal('1100.50'),
                'stock': 50,
                'categoria': cat_zahumerios
            },
            {
                'nombre': 'Zahumerio de Palo Santo Orgánico',
                'descripcion': 'Varillas de palo santo puro recolectado sustentablemente.',
                'precio': Decimal('1500.00'),
                'stock': 120,
                'categoria': cat_zahumerios
            }
        ]

        # Crear Productos para Velas
        productos_velas = [
            {
                'nombre': 'Vela de Soja Vainilla y Coco',
                'descripcion': 'Vela artesanal en frasco de vidrio. 200g.',
                'precio': Decimal('3200.00'),
                'stock': 30,
                'categoria': cat_velas
            },
            {
                'nombre': 'Vela Energética de Canela',
                'descripcion': 'Vela roja intencionada para la abundancia.',
                'precio': Decimal('1800.00'),
                'stock': 45,
                'categoria': cat_velas
            },
            {
                'nombre': 'Vela Alquímica Nube Azul',
                'descripcion': 'Vela de cera de abeja con aroma a flores blancas.',
                'precio': Decimal('4500.00'),
                'stock': 15,
                'categoria': cat_velas
            }
        ]

        # Crear Productos para Sahumos
        productos_sahumos = [
            {
                'nombre': 'Atado de Salvia Blanca',
                'descripcion': 'Para limpiezas energéticas de ambientes y personas.',
                'precio': Decimal('2200.00'),
                'stock': 40,
                'categoria': cat_sahumos
            },
            {
                'nombre': 'Mix de Resinas Sagradas',
                'descripcion': 'Copas de incienso, mirra y benjuí para defumación.',
                'precio': Decimal('3500.00'),
                'stock': 20,
                'categoria': cat_sahumos
            }
        ]

        todos_los_productos = productos_zahumerios + productos_velas + productos_sahumos

        for p_data in todos_los_productos:
            producto, creado = Producto.objects.update_or_create(
                nombre=p_data['nombre'],
                defaults={
                    'descripcion': p_data['descripcion'],
                    'precio': p_data['precio'],
                    'stock': p_data['stock'],
                    'categoria': p_data['categoria']
                }
            )
            if creado:
                self.stdout.write(self.style.SUCCESS(f'Producto creado: {producto.nombre}'))
            else:
                self.stdout.write(f'Producto actualizado: {producto.nombre}')

        self.stdout.write(self.style.SUCCESS('Población completada exitosamente.'))
