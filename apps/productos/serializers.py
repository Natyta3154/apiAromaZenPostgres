from rest_framework import serializers
from .models import Producto, Categoria

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']

class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')
    imagen = serializers.ReadOnlyField(source='imagen_url')
    rating = serializers.SerializerMethodField()
    num_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'precio', 
            'stock', 'categoria', 'categoria_nombre', 
            'imagen', 'activo', 'rating', 'num_reviews'
        ]

    def get_rating(self, obj):
        from django.db.models import Avg
        # Calculamos el promedio de calificacion de las reseñas asociadas
        promedio = obj.reseñas.aggregate(Avg('calificacion'))['calificacion__avg']
        return round(float(promedio), 1) if promedio else 0

    def get_num_reviews(self, obj):
        # Contamos el total de reseñas
        return obj.reseñas.count()
