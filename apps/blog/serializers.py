from rest_framework import serializers
from .models import Articulo
from apps.comentarios.models import Reseña

class ArticuloSerializer(serializers.ModelSerializer):
    imagen = serializers.ReadOnlyField(source='imagen_portada')
    
    class Meta:
        model = Articulo
        fields = ['id', 'titulo', 'slug', 'contenido', 'imagen', 'fecha_publicacion']

class TestimonioSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    puntuacion = serializers.ReadOnlyField(source='calificacion')
    fecha = serializers.ReadOnlyField(source='fecha_creacion')
    
    class Meta:
        model = Reseña
        fields = ['id', 'usuario_nombre', 'comentario', 'puntuacion', 'fecha']
