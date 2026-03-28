from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Producto, Categoria
from .serializers import ProductoSerializer, CategoriaSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    """
    Vista para ver, crear, editar y eliminar productos.
    """
    queryset = Producto.objects.filter(activo=True)
    serializer_class = ProductoSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'destacados']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def destacados(self, request):
        destacados = self.queryset.filter(destacado=True)[:5]
        serializer = self.get_serializer(destacados, many=True)
        return Response(serializer.data)

class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vista de solo lectura para categorías.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.AllowAny]
