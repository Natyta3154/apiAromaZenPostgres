from django.db import models
from django.conf import settings
from apps.productos.models import Producto

class Orden(models.Model):
    """
    Representa una compra finalizada o en proceso.
    Aquí se guardan los datos del cliente, el total a pagar y la dirección de envío.
    """
    ESTADOS = [
        ('pendiente', 'Pendiente de Pago'),
        ('pagado', 'Pago Confirmado'),
        ('procesando', 'Pendiente de Envío'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ordenes', verbose_name="Cliente")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Compra")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente', verbose_name="Estado")
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total")
    id_transaccion_mp = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID Mercado Pago")
    
    # Datos de logística (Dirección donde llegará el producto)
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    ciudad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ciudad")
    provincia = models.CharField(max_length=100, blank=True, null=True, verbose_name="Provincia")
    codigo_postal = models.CharField(max_length=20, blank=True, null=True, verbose_name="Código Postal")
    telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name="Teléfono")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas de Envío")
    
    codigo_seguimiento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Código de Seguimiento")
    empresa_envio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Empresa de Envío")

    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Orden #{self.id} - {self.usuario.username}"

    @property
    def resumen_productos(self):
        """Genera un resumen corto de los productos para mostrar en el panel principal del admin."""
        detalles = self.detalles.all()
        resumen = ", ".join([f"{d.cantidad}x {d.producto.nombre}" for d in detalles])
        if len(resumen) > 50:
            return resumen[:47] + "..."
        return resumen or "Sin productos"

    @property
    def detalle_productos_html(self):
        """Formatea la lista de productos en HTML para que se vea bien en el formulario del administrador."""
        from django.utils.html import format_html
        from django.utils.safestring import mark_safe
        
        detalles = self.detalles.all()
        if not detalles.exists():
            return mark_safe('<span style="color: #e74c3c;">⚠️ No hay productos registrados</span>')
        
        items_html = []
        for d in detalles:
            precio_fmt = f"${float(d.precio_unitario):,.2f}"
            items_html.append(
                format_html(
                    '<li style="margin-bottom: 5px;">'
                    '<b style="color: #2c3e50;">{}x</b> {} '
                    '<span style="color: #7f8c8d; margin-left: 10px;">({})</span>'
                    '</li>',
                    d.cantidad, d.producto.nombre, precio_fmt
                )
            )
        
        return mark_safe(
            '<div style="background: #f8f9fa; padding: 10px; border-radius: 5px; border: 1px solid #dee2e6;">'
            '<ul style="margin: 0; padding-left: 20px; list-style-type: square;">' 
            + "".join(items_html) + 
            '</ul></div>'
        )

class DetalleOrden(models.Model):
    """
    Renglón de la factura. Registra qué producto y a qué precio se vendió en ESA orden específica.
    Es importante guardar el precio unitario aquí por si el producto cambia de precio en el catálogo después.
    """
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='detalles', verbose_name="Orden")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, verbose_name="Producto")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    
    @property
    def subtotal(self):
        """Precio unitario x Cantidad para este renglón."""
        if not self.cantidad or not self.precio_unitario:
            return 0
        return self.cantidad * self.precio_unitario

    class Meta:
        verbose_name = "Detalle de Orden"
        verbose_name_plural = "Detalles de Órdenes"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
