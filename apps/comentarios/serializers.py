from rest_framework import serializers
from .models import Reseña, MensajeContacto

class ReseñaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.ReadOnlyField(source='usuario.username')
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')

    class Meta:
        model = Reseña
        fields = [
            'id', 'usuario', 'usuario_nombre', 'producto', 
            'producto_nombre', 'comentario', 'calificacion', 
            'destacado_home', 'fecha_creacion'
        ]
        read_only_fields = ['destacado_home']


class MensajeContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MensajeContacto
        fields = ['id', 'nombre', 'email', 'tipo', 'asunto', 'mensaje', 'fecha_creacion']
        read_only_fields = ['fecha_creacion']
