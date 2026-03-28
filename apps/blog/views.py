from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Articulo
from .serializers import ArticuloSerializer, TestimonioSerializer
from apps.comentarios.models import Reseña

class ArticuloViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vista de solo lectura para los artículos del blog.
    """
    queryset = Articulo.objects.filter(activo=True)
    serializer_class = ArticuloSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def testimonios(request):
    """
    Vista para obtener testimonios destacados para el home.
    """
    reseñas = Reseña.objects.filter(destacado_home=True)[:6]
    serializer = TestimonioSerializer(reseñas, many=True)
    return Response(serializer.data)
