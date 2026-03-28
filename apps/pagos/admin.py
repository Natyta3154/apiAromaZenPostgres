import json
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import Pago, CompraLog

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id_transaccion_mp', 'cliente_detalle', 'ir_a_orden', 'monto_formateado', 'estado_badge', 'fecha_pago')
    list_filter = ('estado', 'fecha_pago')
    search_fields = ('id_transaccion_mp', 'orden__id', 'orden__usuario__username', 'orden__usuario__email')
    
    fieldsets = (
        ('💳 Información de la Transacción', {
            'fields': ('id_transaccion_mp', 'monto_formateado', 'estado_badge', 'fecha_pago')
        }),
        ('📦 Relación Comercial', {
            'fields': ('cliente_detalle', 'orden', 'ir_a_orden', 'info_envio'),
        }),
        ('🛍️ Productos Adquiridos', {
            'fields': ('productos_adquiridos',),
        }),
        ('🛠️ Datos Técnicos', {
            'fields': ('datos_crudos_formateados',),
            'classes': ('collapse',),
            'description': "Información cruda de la API para auditoría y soporte."
        }),
    )

    readonly_fields = (
        'cliente_detalle', 'monto_formateado', 'productos_adquiridos', 
        'id_transaccion_mp', 'ir_a_orden', 'info_envio', 'estado_badge', 
        'fecha_pago', 'datos_crudos_formateados', 'orden'
    )
    exclude = ('datos_crudos', 'monto_total', 'estado')

    def monto_formateado(self, obj):
        try:
            return f"${float(obj.monto_total or 0):,.2f}"
        except:
            return f"${obj.monto_total}"
    monto_formateado.short_description = "Monto Total"

    def estado_badge(self, obj):
        colores = {'pendiente': '#ffc107', 'aprobado': '#28a745', 'rechazado': '#dc3545', 'cancelado': '#6c757d'}
        color = colores.get(obj.estado, '#000')
        return format_html(
            '<span style="color:white; background:{}; padding:3px 10px; border-radius:10px; font-weight:bold;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = "Estado de Pago"

    def productos_adquiridos(self, obj):
        if not obj.orden: return mark_safe('<span style="color:gray;">Sin orden asociada.</span>')
        detalles = obj.orden.detalles.all()
        if not detalles.exists():
            return mark_safe('<span style="color:red;">No hay productos registrados en la orden.</span>')
            
        items = []
        for d in detalles:
            precio_fmt = f"${float(d.precio_unitario):,.2f}"
            items.append(format_html(
                '<div style="margin-bottom:5px; padding:5px; border-bottom:1px solid #eee;">'
                '📦 <b>{}x</b> {} <span style="color:#666; font-size:0.9em;">({})</span>'
                '</div>',
                d.cantidad, d.producto.nombre, precio_fmt
            ))
        return mark_safe("".join(items))
    productos_adquiridos.short_description = "Contenido del Pedido"

    def cliente_detalle(self, obj):
        if not obj.orden or not obj.orden.usuario: return "N/A"
        u = obj.orden.usuario
        nombre = u.get_full_name() or u.username
        return format_html('<b>{}</b><br><small style="color:#666;">{}</small>', nombre, u.email)
    cliente_detalle.short_description = "Cliente"

    def ir_a_orden(self, obj):
        if not obj.orden: return "N/A"
        url = reverse('admin:pedidos_orden_change', args=[obj.orden.id])
        return format_html(
            '<a href="{}" style="font-weight:bold; color:#17a2b8;">'
            '<i class="fas fa-shopping-bag"></i> Ver Pedido #{}'
            '</a>', url, obj.orden.id
        )
    ir_a_orden.short_description = "Vínculo a Pedido"

    def info_envio(self, obj):
        if not obj.orden: return mark_safe('<span style="color:gray;">Sin datos de envío.</span>')
        o = obj.orden
        if not o.direccion:
            return mark_safe('<span style="color:gray;">No se cargaron datos de envío.</span>')
        return format_html(
            '<div style="line-height:1.6;">'
            '📍 <b>Dirección:</b> {}<br>'
            '🏙️ <b>Ciudad:</b> {} ({}) - CP: {}<br>'
            '📞 <b>Teléfono:</b> {}<br>'
            '📝 <b>Notas:</b> {}'
            '</div>', 
            o.direccion, o.ciudad or 'N/A', o.provincia or 'N/A', o.codigo_postal or 'N/A', 
            o.telefono or 'N/A', o.notas or 'Sin notas'
        )
    info_envio.short_description = "Datos de Entrega"

    def datos_crudos_formateados(self, obj):
        if not obj.datos_crudos: return "Sin datos"
        pretty_json = json.dumps(obj.datos_crudos, indent=4, ensure_ascii=False)
        return format_html(
            '<pre style="background: #f8f9fa; padding: 10px; border-radius: 5px; max-height: 400px; overflow-y: auto; border: 1px solid #ddd;">{}</pre>', 
            pretty_json
        )
    datos_crudos_formateados.short_description = "Respuesta JSON Mercado Pago"


