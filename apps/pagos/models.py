from django.db import models
from django.conf import settings

class Pago(models.Model):
    ESTADOS_PAGO = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('cancelado', 'Cancelado'),
    ]

    orden = models.ForeignKey('pedidos.Orden', on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos', verbose_name="Orden Asociada")
    id_transaccion_mp = models.CharField(max_length=200, unique=True, verbose_name="ID de Transacción Mercado Pago")
    estado = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='pendiente', verbose_name="Estado del Pago")
    fecha_pago = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del Pago")
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto Total")
    datos_crudos = models.JSONField(default=dict, blank=True, null=True, verbose_name="Datos Completos de MP")

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"Pago {self.id_transaccion_mp} - {self.estado}"

    def confirmar_pago_exitoso(self):
        """
        Lógica para marcar el pago como aprobado y realizar acciones secundarias.
        """
        self.estado = 'aprobado'
        self.save()

class CompraLog(models.Model):
    """
    Log de auditoría para cambios en órdenes y pagos.
    """
    pedido = models.ForeignKey('pedidos.Orden', on_delete=models.CASCADE, related_name='logs', verbose_name="Pedido")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario (Admin)")
    mensaje = models.TextField(verbose_name="Datos de Envío y Seguimiento")

    class Meta:
        verbose_name = "Log de Compra"
        verbose_name_plural = "Logs de Compras"
        ordering = ['-fecha']

    def __str__(self):
        return f"Log #{self.id} - Orden #{self.pedido.id}"
