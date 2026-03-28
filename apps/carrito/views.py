from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Carrito, ItemCarrito
from .serializers import CarritoSerializer, ItemCarritoSerializer
from apps.productos.models import Producto
from apps.pagos.servicios import MercadoPagoServicio

class CarritoViewSet(viewsets.GenericViewSet):
    """
    ViewSet para gestionar el carrito del usuario autenticado.
    """
    serializer_class = CarritoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Aseguramos que el usuario solo vea SU carrito
        carrito, _ = Carrito.objects.get_or_create(usuario=self.request.user)
        return carrito

    def list(self, request):
        """Devuelve el contenido del carrito actual."""
        carrito = self.get_queryset()
        serializer = self.get_serializer(carrito)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='agregar')
    def agregar_producto(self, request):
        """Agrega un producto al carrito o incrementa su cantidad."""
        producto_id = request.data.get('producto_id')
        cantidad = int(request.data.get('cantidad', 1))

        try:
            producto = Producto.objects.get(id=producto_id, activo=True)
        except Producto.DoesNotExist:
            return Response({"error": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Verificar stock antes de agregar
        if not producto.tiene_stock(cantidad):
            return Response({"error": f"Stock insuficiente. Solo quedan {producto.stock} unidades."}, status=status.HTTP_400_BAD_REQUEST)

        carrito = self.get_queryset()
        item, creado = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
        
        if not creado:
            # Si ya existía, verificamos si la suma de lo que hay + lo nuevo excede el stock
            nueva_cantidad = item.cantidad + cantidad
            if not producto.tiene_stock(nueva_cantidad):
                return Response({"error": "No puedes agregar más unidades de las disponibles en stock."}, status=status.HTTP_400_BAD_REQUEST)
            item.cantidad = nueva_cantidad
        else:
            item.cantidad = cantidad
        
        item.save()
        return Response({"mensaje": f"{producto.nombre} agregado al carrito."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], url_path='vaciar')
    def vaciar_carrito(self, request):
        """Elimina todos los productos del carrito."""
        carrito = self.get_queryset()
        carrito.items.all().delete()
        return Response({"mensaje": "Carrito vaciado correctamente."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='quitar')
    def quitar_producto(self, request):
        """Elimina un producto específico o reduce su cantidad."""
        producto_id = request.data.get('producto_id')
        
        carrito = self.get_queryset()
        try:
            item = ItemCarrito.objects.get(carrito=carrito, producto_id=producto_id)
            item.delete()
            return Response({"mensaje": "Producto eliminado del carrito."}, status=status.HTTP_200_OK)
        except ItemCarrito.DoesNotExist:
            return Response({"error": "El producto no está en tu carrito."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='finalizar-compra')
    def finalizar_compra(self, request):
        """
        Inicia el proceso de pago generando una preferencia en Mercado Pago.
        """
        carrito = self.get_queryset()
        
        if not carrito.items.exists():
            return Response({"error": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        # Usamos el servicio de Mercado Pago para crear el link de pago
        mp_servicio = MercadoPagoServicio()
        try:
            preferencia = mp_servicio.crear_preferencia_pago(carrito, request.user)
            return Response({
                "mensaje": "Preferencia de pago creada.",
                "url_pago": preferencia["url_pago"],
                "id_preferencia": preferencia["preference_id"]
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "error": "Error al comunicar con Mercado Pago.",
                "detalle": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
