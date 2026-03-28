from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import redirect
from django.conf import settings as django_settings
from .servicios import MercadoPagoServicio
from apps.carrito.models import Carrito

class CrearPreferenciaPagoView(APIView):
    """
    Crea una preferencia de pago en Mercado Pago para el carrito del usuario.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Sincronizamos el carrito local del frontend con la base de datos
            items_data = request.data.get('items', [])
            if not items_data:
                return Response(
                    {"error": "El carrito está vacío o no se enviaron items"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Obtener o crear el carrito del usuario
            carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
            
            # Limpiar items anteriores para sincronizar con el estado actual del frontend
            carrito.items.all().delete()
            
            from apps.productos.models import Producto
            from apps.carrito.models import ItemCarrito
            
            for item in items_data:
                producto = Producto.objects.filter(id=item.get('producto_id')).first()
                if producto:
                    ItemCarrito.objects.create(
                        carrito=carrito,
                        producto=producto,
                        cantidad=item.get('cantidad', 1)
                    )

            if not carrito.items.exists():
                return Response(
                    {"error": "No se pudieron procesar los productos del carrito"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Extraemos los datos de envío si los hay
            datos_envio = request.data.get('envio', {})

            mp_servicio = MercadoPagoServicio()
            resultado = mp_servicio.crear_preferencia_pago(carrito, request.user, datos_envio)
            
            return Response(resultado, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            print(f"\n❌ ERROR EN CHECKOUT: {str(e)}")
            traceback.print_exc()
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MercadoPagoWebhookView(APIView):
    """
    Endpoint para recibir notificaciones (IPN) de Mercado Pago.
    """
    permission_classes = []  # Mercado Pago envía notificaciones sin autenticación Bearer

    def post(self, request, *args, **kwargs):
        # En una implementación real, aquí se verificaría la autenticidad con la clave secreta
        datos = request.data
        
        mp_servicio = MercadoPagoServicio()
        procesado = mp_servicio.procesar_webhook_notificacion(datos)
        
        if procesado:
            return Response({"mensaje": "Notificación procesada."}, status=status.HTTP_200_OK)
        
        # Siempre respondemos 200/201 a MP para evitar reintentos infinitos si el tópico no nos interesa
        return Response({"mensaje": "Tópico ignorado."}, status=status.HTTP_200_OK)


class ConfirmarPagoView(APIView):
    """
    El frontend llama a este endpoint al llegar a la página de éxito,
    pasando el payment_id que MercadoPago incluye en la URL de retorno.
    Esto registra el pago en la BD sin depender del webhook (útil en localhost).
    """
    permission_classes = []  # Público: el payment_id es validado directamente con la API de MP

    def post(self, request):
        payment_id = request.data.get("payment_id")
        if not payment_id:
            return Response(
                {"error": "Se requiere payment_id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            mp_servicio = MercadoPagoServicio()
            resultado = mp_servicio.consultar_pago_por_id(payment_id)

            if not resultado:
                return Response(
                    {"error": "No se pudo obtener información del pago desde MercadoPago"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(resultado, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RetornoMercadoPagoView(APIView):
    """
    MP redirige aquí (GET) luego del pago.
    Registramos el pago y redirigimos al frontend.
    No necesita HTTPS — apunta a Django en localhost:8000.
    """
    permission_classes = []  # MP no envía credenciales

    def get(self, request):
        payment_id = request.query_params.get("payment_id")
        mp_status  = request.query_params.get("status")

        # URL base del frontend (React en localhost:5173 por defecto)
        frontend_url = getattr(django_settings, 'FRONTEND_URL', 'http://localhost:5173')

        if mp_status == "approved" and payment_id:
            try:
                mp_servicio = MercadoPagoServicio()
                mp_servicio.consultar_pago_por_id(payment_id)
                print(f"✅ Retorno MP: pago {payment_id} registrado.")
            except Exception as e:
                print(f"⚠️  Retorno MP: error al registrar pago {payment_id}: {e}")

            return redirect(f"{frontend_url}/success?payment_id={payment_id}&status=approved")

        # Pago rechazado o pendiente
        return redirect(f"{frontend_url}/carrito?status={mp_status or 'failure'}")
