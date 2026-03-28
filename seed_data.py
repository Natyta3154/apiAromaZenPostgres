#es para agregar productyos ala base de datos cuando no hay nada



import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.productos.models import Categoria, Producto
from apps.blog.models import Articulo
from apps.comentarios.models import Reseña
from decimal import Decimal

def seed():
    print("🌱 Sembrando datos...")

    # 1. Crear Superusuario si no existe
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("👤 Superusuario creado (admin/admin123)")

    user = User.objects.first()

    # 2. Categorías
    cats = [
        ('Sahumerios', 'Inciensos artesanales de alta calidad'),
        ('Velas', 'Velas de soja aromáticas'),
        ('Resinas', 'Resinas puras para defumación'),
    ]
    for nombre, desc in cats:
        Categoria.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})

    cat_sahumerio = Categoria.objects.get(nombre='Sahumerios')

    # 3. Productos (con campo destacado)
    productos = [
        {
            'nombre': 'Sándalo Hindú',
            'descripcion': 'Sahumerio premium con notas amaderadas intensas.',
            'precio': Decimal('1500.00'),
            'stock': 50,
            'categoria': cat_sahumerio,
            'imagen_url': 'https://images.unsplash.com/photo-1602928321679-560bb453f190?w=500',
            'destacado': True
        },
        {
            'nombre': 'Lavanda Relajante',
            'descripcion': 'Ideal para meditación y momentos de paz.',
            'precio': Decimal('1200.00'),
            'stock': 30,
            'categoria': cat_sahumerio,
            'imagen_url': 'https://images.unsplash.com/photo-1612454157121-867372d8977c?w=500',
            'destacado': True
        },
        {
            'nombre': 'Palo Santo Natural',
            'descripcion': 'Limpieza energética profunda.',
            'precio': Decimal('1800.00'),
            'stock': 20,
            'categoria': cat_sahumerio,
            'imagen_url': 'https://images.unsplash.com/photo-1616031037011-087000171abe?w=500',
            'destacado': True
        },
        {
            'nombre': 'Sahumerio de Rosas',
            'descripcion': 'Aroma dulce y romántico para tu hogar.',
            'precio': Decimal('1300.00'),
            'stock': 40,
            'categoria': cat_sahumerio,
            'imagen_url': 'https://images.unsplash.com/photo-1594913366159-1832006346be?w=500',
            'destacado': True
        },
        {
            'nombre': 'Incienso de Copal',
            'descripcion': 'Antigua resina sagrada de México.',
            'precio': Decimal('1650.00'),
            'stock': 15,
            'categoria': cat_sahumerio,
            'imagen_url': 'https://images.unsplash.com/photo-1570111100371-fd76962f3a69?w=500',
            'destacado': True
        },
    ]

    for p_data in productos:
        Producto.objects.update_or_create(nombre=p_data['nombre'], defaults=p_data)
    
    print("🛍️ Productos y categorías sembrados")

    # 4. Blog
    articulos = [
        {
            'titulo': 'Los beneficios del Palo Santo',
            'contenido': '<p>El palo santo es conocido por sus propiedades de limpieza energética...</p>',
            'imagen_portada': 'https://images.unsplash.com/photo-1616031037011-087000171abe?w=800',
        },
        {
            'titulo': 'Cómo meditar con incienso',
            'contenido': '<p>Crear el ambiente perfecto es clave para una buena meditación...</p>',
            'imagen_portada': 'https://images.unsplash.com/photo-1602928321679-560bb453f190?w=800',
        }
    ]
    for a_data in articulos:
        Articulo.objects.get_or_create(titulo=a_data['titulo'], defaults=a_data)
    
    print("📝 Blog sembrado")

    # 5. Reseñas (Testimonios)
    reseñas = [
        {
            'usuario': user,
            'producto': Producto.objects.first(),
            'comentario': 'Los mejores sahumerios que he probado. El aroma a sándalo es increíble.',
            'calificacion': 5,
            'destacado_home': True
        },
        {
            'usuario': user,
            'producto': Producto.objects.last(),
            'comentario': 'La presentación es hermosa y el envío fue muy rápido.',
            'calificacion': 4,
            'destacado_home': True
        }
    ]
    for r_data in reseñas:
        Reseña.objects.get_or_create(comentario=r_data['comentario'], defaults=r_data)

    print("⭐ Testimonios sembrados")
    print("✨ Proceso completado con éxito.")

if __name__ == '__main__':
    seed()
