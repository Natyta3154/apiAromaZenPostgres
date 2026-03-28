import mercadopago
from django.conf import settings
from django.db import transaction
from .models import Pago, CompraLog
from apps.pedidos.models import Orden, DetalleOrden
from apps.productos.models import Producto
from apps.carrito.models import Carrito

# Mapeo del estado de MP (inglés) al choices del modelo (español)
MAPA_ESTADOS_MP = {
    'approved':  'aprobado',
    'rejected':  'rechazado',
    'pending':   'pendiente',
    'cancelled': 'cancelado',
    'in_process': 'pendiente',
    'authorized': 'pendiente',
}

class MercadoPagoServicio:
    """
    Servicio encargado de la integración con Mercado Pago y gestión de pedidos.
    """

    def __init__(self):
        """
        Inicia la conexión con la API de Mercado Pago usando tu Token de Acceso.
        El token se configura en el archivo .env como MP_ACCESS_TOKEN.
        """
        token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', None)
        if not token:
            raise ValueError("Error de configuración: MERCADOPAGO_ACCESS_TOKEN no encontrado.")
        self.sdk = mercadopago.SDK(token)

    def crear_preferencia_pago(self, carrito, usuario, datos_envio=None):
        """
        Crea una Orden en la BD y genera la preferencia de Mercado Pago.
        """
        with transaction.atomic():
            # 0. Limpiar órdenes previas en estado 'pendiente' para evitar acumulación
            # Solo eliminamos las que no tienen ID de transacción MP asociado
            Orden.objects.filter(
                usuario=usuario, 
                estado='pendiente', 
                id_transaccion_mp__isnull=True
            ).delete()

            # 1. Crear la Orden (estado inicial: pendiente)
            # Extraemos los datos de envío validados o enviamos vacío
            shipping_data = {
                'direccion': datos_envio.get('direccion') if datos_envio else None,
                'ciudad': datos_envio.get('ciudad') if datos_envio else None,
                'provincia': datos_envio.get('provincia') if datos_envio else None,
                'codigo_postal': datos_envio.get('codigo_postal') if datos_envio else None,
                'telefono': datos_envio.get('telefono') if datos_envio else None,
                'notas': datos_envio.get('notas') if datos_envio else None,
            }
            
            orden = Orden.objects.create(
                usuario=usuario,
                total=carrito.total,
                estado='pendiente',
                **shipping_data
            )

            items_pago = []
            for item in carrito.items.all():
                # Bloquear el producto para asegurar stock durante la transacción
                producto = Producto.objects.select_for_update().get(id=item.producto.id)
                
                if not producto.tiene_stock(item.cantidad):
                    raise ValueError(f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}")

                # Crear el detalle de la orden (snapshot de precio)
                DetalleOrden.objects.create(
                    orden=orden,
                    producto=producto,
                    cantidad=item.cantidad,
                    precio_unitario=producto.precio
                )

                # Preparar item para Mercado Pago con descripción detallada
                items_pago.append({
                    "title": producto.nombre,
                    "description": producto.descripcion[:250] if producto.descripcion else producto.nombre,
                    "quantity": item.cantidad,
                    "unit_price": float(producto.precio),
                    "currency_id": "ARS"
                })

            # 2. Configurar datos de la preferencia
            datos_preferencia = {
                "items": items_pago,
                "payer": {
                    "email": usuario.email,
                    "name": usuario.get_full_name(),
                },
                "back_urls": {
                    "success": f"{settings.FRONTEND_URL}/success",
                    "failure": f"{settings.FRONTEND_URL}/carrito",
                    "pending": f"{settings.FRONTEND_URL}/carrito"
                },
                # Comentado 'auto_return' para evitar error 'invalid_auto_return' en localhost
                # "auto_return": "approved", 
                "notification_url": getattr(settings, 'MERCADOPAGO_WEBHOOK_URL', None),
                "external_reference": str(orden.id)
            }

            # 3. Llamar al SDK de Mercado Pago
            resultado = self.sdk.preference().create(datos_preferencia)
            respuesta = resultado.get("response")

            if not respuesta or "id" not in respuesta:
                error_msg = respuesta.get("message", "Error desconocido de Mercado Pago") if respuesta else "No hubo respuesta del SDK"
                raise Exception(f"Error al crear preferencia: {error_msg}")

            # Crear Log de Auditoría inicial
            CompraLog.objects.create(
                pedido=orden,
                mensaje="Preferencia de pago creada en Mercado Pago. Esperando confirmación.",
                usuario=usuario
            )

            return {
                "preference_id": respuesta["id"],
                "url_pago": respuesta["init_point"],
                "orden_id": orden.id,
                "total": float(orden.total)
            }

    def procesar_webhook_notificacion(self, datos_notificacion):
        """
        Recibe y valida las notificaciones automáticas (webhooks) de Mercado Pago.
        Se activa cada vez que un cliente paga.
        """
        tipo = datos_notificacion.get("type") or datos_notificacion.get("topic")
        
        if tipo == "payment":
            # Extraemos el ID del pago que nos manda Mercado Pago
            id_pago = datos_notificacion.get("data", {}).get("id") or datos_notificacion.get("id")
            # Consultamos los detalles completos del pago a MP para seguridad
            info_pago = self.sdk.payment().get(id_pago)
            respuesta = info_pago["response"]

            estado_mp = respuesta.get("status", "pendiente") # EJ: approved, rejected, pending
            orden_id = respuesta.get("external_reference") # El ID de nuestra orden
            monto = respuesta.get("transaction_amount", 0)

            # Siguiente paso: actualizar el estado en nuestra BD
            self._actualizar_estado_pago(orden_id, estado_mp, id_pago, respuesta, monto)
            return True
        return False

    def _actualizar_estado_pago(self, orden_id, estado_mp, mp_id_pago, datos_crudos, monto=0):
        """
        Lógica interna que reconcilia el estado de MP con nuestra base de datos.
        Aquí es donde se descuenta el stock REAL cuando el pago se aprueba.
        """
        print(f"📡 Procesando pago MP {mp_id_pago} para Orden {orden_id}. Estado recibido: {estado_mp}")
        estado_local = MAPA_ESTADOS_MP.get(estado_mp, 'pendiente')

        with transaction.atomic():
            try:
                # Buscamos la orden en blanco y la bloqueamos para evitar errores por duplicado
                orden = Orden.objects.select_for_update().get(id=orden_id)
                print(f"📦 Orden {orden.id} encontrada. Estado actual: {orden.estado}")
            except (Orden.DoesNotExist, ValueError):
                print(f"⚠️ Orden con ID {orden_id} no encontrada.")
                return

            # Registramos el pago en nuestra tabla 'Pago' para historial
            pago, created = Pago.objects.get_or_create(
                id_transaccion_mp=str(mp_id_pago),
                defaults={
                    "orden": orden, 
                    "monto_total": monto,
                    "estado": estado_local,
                    "datos_crudos": datos_crudos
                }
            )
            if not created:
                pago.orden = orden
                pago.estado = estado_local
                pago.datos_crudos = datos_crudos
                pago.save()

            # SI EL PAGO FUE APROBADO:
            if estado_mp == "approved":
                if orden.estado != 'pagado':
                    print(f"✅ Pago APROBADO. Actualizando Orden {orden.id} a 'pagado'.")
                    orden.estado = 'pagado'
                    orden.id_transaccion_mp = str(mp_id_pago)
                    orden.save()

                    # DESCUENTO DE STOCK DEFINITIVO (Paso crítico)
                    for detalle in orden.detalles.all():
                        # Bloqueamos el producto para evitar inconsistencias
                        producto = Producto.objects.select_for_update().get(id=detalle.producto.id)
                        
                        if producto.stock >= detalle.cantidad:
                            producto.stock -= detalle.cantidad
                            producto.save()
                            print(f"📉 Stock descontado: {producto.nombre} (-{detalle.cantidad})")
                        else:
                            # Alertamos si el stock se acabó justo en el proceso
                            print(f"🚨 ERROR CRÍTICO: Pago aprobado pero NO hay stock suficiente para {producto.nombre}.")
                    
                    # Vaciamos el carrito del cliente tras la compra exitosa
                    try:
                        carrito, created = Carrito.objects.get_or_create(usuario=orden.usuario)
                        items_borrados = carrito.items.all().delete()
                        print(f"🛒 Carrito vaciado con éxito.")
                    except Exception as e:
                        print(f"⚠️ Error al vaciar el carrito: {e}")

                    pago.confirmar_pago_exitoso()
                    
                    # Guardamos la bitácora del evento
                    CompraLog.objects.create(
                        pedido=orden,
                        mensaje=f"✅ Pago APROBADO vía MP (ID: {mp_id_pago}). Monto: ${monto}",
                        usuario=None 
                    )
                else:
                    print(f"ℹ️ La Orden {orden.id} ya había sido procesada como pagada.")
            
            # SI EL PAGO FUE RECHAZADO O CANCELADO:
            elif estado_mp in ['rejected', 'cancelled']:
                print(f"❌ Pago fallido ({estado_mp}). Cancelando pedido {orden.id}.")
                orden.estado = 'cancelado'
                orden.save()
                pago.estado = estado_local
                pago.save()

                # Guardamos en la bitácora la cancelación
                CompraLog.objects.create(
                    pedido=orden,
                    mensaje=f"❌ Pago {estado_mp.upper()} vía Mercado Pago (ID: {mp_id_pago}).",
                    usuario=None
                )
            else:
                print(f"⏳ Pago pendiente de resolución en MP (Estado: {estado_mp}).")

    def consultar_pago_por_id(self, id_pago_mp):
        """
        Consulta manual a Mercado Pago usando el ID del pago.
        Útil para depurar o si el webhook nunca llegó.
        """
        try:
            info = self.sdk.payment().get(id_pago_mp)
            respuesta = info.get("response", {})
            
            if not respuesta or "status" not in respuesta:
                print(f"⚠️ No se encontró respuesta para el pago MP {id_pago_mp}")
                return None

            estado_mp = respuesta.get("status", "pendiente")
            orden_id = respuesta.get("external_reference")
            monto = respuesta.get("transaction_amount", 0)

            print(f"🔍 Consultando Pago MP {id_pago_mp}. Orden asociada: {orden_id}. Estado: {estado_mp}")
            # Sincronizamos el estado encontrado con nuestra BD
            self._actualizar_estado_pago(orden_id, estado_mp, id_pago_mp, respuesta, monto)

            return {
                "id": id_pago_mp,
                "estado": MAPA_ESTADOS_MP.get(estado_mp, 'pendiente'),
                "monto": monto,
                "orden_id": orden_id
            }
        except Exception as e:
            print(f"❌ Error al consultar pago MP {id_pago_mp}: {e}")
            return None

    def consultar_pago_por_orden(self, orden_id):
        """
        Busca en los servidores de Mercado Pago si existe algún pago para una Orden específica.
        Esto ayuda a recuperar pagos que quedaron en el 'limbo' del servidor de MP.
        """
        filtros = {
            "external_reference": str(orden_id),
            "sort": "date_created",
            "criteria": "desc"
        }
        
        resultado = self.sdk.payment().search(filtros)
        respuesta = resultado.get("response", {})
        results = respuesta.get("results", [])

        if not results:
            print(f"ℹ️ No se encontraron pagos en MP para la Orden {orden_id}")
            return None

        # Tomamos el pago más reciente aprobado o el último que aparezca
        pago_data = next((p for p in results if p.get("status") == "approved"), results[0])
        
        mp_id_pago = pago_data.get("id")
        estado_mp = pago_data.get("status")
        monto = pago_data.get("transaction_amount", 0)

        print(f"🔄 Sincronizando: Orden {orden_id} -> Encontrado pago MP {mp_id_pago} (Estado: {estado_mp})")
        self._actualizar_estado_pago(orden_id, estado_mp, mp_id_pago, pago_data, monto)
        
        return {
            "id": mp_id_pago,
            "estado": MAPA_ESTADOS_MP.get(estado_mp, 'pendiente'),
            "monto": monto
        }
