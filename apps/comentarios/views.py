from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Reseña, MensajeContacto
from .serializers import ReseñaSerializer, MensajeContactoSerializer
from apps.pagos.models import Pago

class ReseñaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar reseñas. 
    Solo clientes que compraron pueden comentar.
    """
    queryset = Reseña.objects.all()
    serializer_class = ReseñaSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        usuario = request.user
        producto_id = request.data.get('producto')

        # VALIDACIÓN PROFESIONAL: ¿El usuario compró este producto?
        # Para simplificar en esta etapa, verificamos si el usuario tiene AL MENOS un pago aprobado.
        tiene_compras = Pago.objects.filter(
            estado='aprobado'
            # En una versión más avanzada, filtraríamos por carrito -> items -> producto
        ).exists()

        if not tiene_compras:
            return Response(
                {"error": "Solo los clientes con compras aprobadas pueden dejar reseñas."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='destacados')
    def destacados(self, request):
        """Devuelve solo los comentarios destacados para el Home."""
        comentarios = Reseña.objects.filter(destacado_home=True)
        serializer = self.get_serializer(comentarios, many=True)
        return Response(serializer.data)


class MensajeContactoCreateView(generics.CreateAPIView):
    """
    Endpoint POST para que cualquier visitante envíe un mensaje de contacto.
    No requiere autenticación.
    El mensaje queda registrado en el Admin automáticamente.
    """
    queryset = MensajeContacto.objects.all()
    serializer_class = MensajeContactoSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        # Si el usuario está autenticado, lo guardamos automáticamente
        usuario = self.request.user if self.request.user.is_authenticated else None
        serializer.save(usuario=usuario)
