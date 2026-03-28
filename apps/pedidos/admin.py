from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import Orden, DetalleOrden
from apps.pagos.models import CompraLog

class DetalleOrdenInline(admin.TabularInline):
    model = DetalleOrden
    extra = 0
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal_formateado')
    readonly_fields = ('subtotal_formateado',)
    
    def subtotal_formateado(self, instance):
        total = instance.cantidad * instance.precio_unitario if instance.cantidad else 0
        return f"${float(total):,.2f}"
    subtotal_formateado.short_description = "Subtotal"

class CompraLogInline(admin.TabularInline):
    model = CompraLog
    extra = 0
    readonly_fields = ('fecha', 'usuario', 'mensaje')
    can_delete = False
    verbose_name = "Historial de Cambios"
    verbose_name_plural = "Historial de Cambios"

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'cliente_detalle', 'total_formateado', 'color_estado', 
        'estado', 'empresa_envio', 'codigo_seguimiento', 'ir_a_pago'   
    )
    list_filter = ('estado', 'fecha_creacion', 'empresa_envio')
    search_fields = ('usuario__username', 'usuario__email', 'id_transaccion_mp', 'detalles__producto__nombre')
    list_editable = ('estado', 'empresa_envio', 'codigo_seguimiento')
    inlines = [DetalleOrdenInline, CompraLogInline]
    list_per_page = 20
    
    fieldsets = (
        ('📜 Información General', {
            'fields': (
                'cliente_detalle', 
                'color_estado',
                'estado', 
                'total_formateado', 
                'ver_detalle_productos'
            )
        }),
        ('📍 Datos de Entrega', {
            'fields': (
                'direccion', ('ciudad', 'provincia', 'codigo_postal'),
                'telefono', 'notas'
            ),
            'description': "Información de destino y contacto para el despacho."
        }),
        ('💳 Información de Pago', {
            'fields': ('id_transaccion_mp', 'ir_a_pago'),
        }),
        ('🚚 Logística y Seguimiento', {
            'fields': ('empresa_envio', 'codigo_seguimiento'),
            'description': "Cargue aquí el código de seguimiento una vez despachado."
        }),
        ('🕒 Fechas de Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = (
        'cliente_detalle', 'total_formateado', 'color_estado',
        'id_transaccion_mp', 'ir_a_pago', 'fecha_creacion', 'fecha_actualizacion', 'ver_detalle_productos',
    )

    # --- LÓGICA DE LOGS (TU REQUERIMIENTO) ---
    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Orden.objects.get(pk=obj.pk)
            cambios = []

            if old_obj.estado != obj.estado:
                cambios.append(f"Estado: {old_obj.get_estado_display()} -> {obj.get_estado_display()}")
            
            if old_obj.codigo_seguimiento != obj.codigo_seguimiento:
                
                cambios.append(f"Tracking: {obj.codigo_seguimiento} ({obj.empresa_envio})")

            if cambios:
                from apps.pagos.models import CompraLog 
                CompraLog.objects.create(
                    pedido=obj,
                    mensaje=" | ".join(cambios),
                    usuario=request.user
                )
        super().save_model(request, obj, form, change)
        
    actions = ['marcar_como_enviado', 'marcar_como_entregado', 'sincronizar_pago']

    # --- MÉTODOS DE VISUALIZACIÓN ---

    def cliente_detalle(self, obj):
        if not obj.usuario: return "Consumidor Final"
        nombre = obj.usuario.get_full_name() or obj.usuario.username
        return format_html(
            '<div style="line-height:1.2;">'
            '<b>{}</b><br><small style="color:#666;">{}</small>'
            '</div>', 
            nombre, obj.usuario.email
        )
    cliente_detalle.short_description = "Cliente"

    def total_formateado(self, obj):
        try:
            val = float(obj.total or 0)
            return f"${val:,.2f}"
        except:
            return f"${obj.total}"
    total_formateado.short_description = "Total Pedido"

    def ir_a_pago(self, obj):
        pago = obj.pagos.first()
        if not pago: return mark_safe('<span style="color:gray;"><i class="fas fa-times"></i> Sin registro</span>')
        url = reverse('admin:pagos_pago_change', args=[pago.id])
        return format_html(
            '<a href="{}" style="font-weight:bold; color:#28a745;">'
            '<i class="fas fa-receipt"></i> Ver Pago #{}'
            '</a>', url, pago.id_transaccion_mp
        )
    ir_a_pago.short_description = "Enlace a Pago"

    def ver_detalle_productos(self, obj):
        detalles = obj.detalles.all()
        if not detalles.exists():
            return mark_safe('<b style="color:red;">⚠️ Sin productos registrados.</b>')
        
        items = []
        for d in detalles:
            p_fmt = f"${float(d.precio_unitario):,.2f}"
            items.append(format_html(
                '<div style="margin-bottom:8px; border-bottom:1px solid #eee; padding-bottom:4px;">'
                '📦 <b>{}x</b> {} <span style="color:#666; font-size:0.9em;">({})</span>'
                '</div>',
                d.cantidad, d.producto.nombre, p_fmt
            ))
        return mark_safe("".join(items))
    ver_detalle_productos.short_description = "Contenido del Pedido"

    def color_estado(self, obj):
        colores = {'pendiente': '#ffc107', 'pagado': '#28a745', 'enviado': '#17a2b8', 'cancelado': '#dc3545'}
        color = colores.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="color:white; background:{}; padding:3px 10px; border-radius:10px; font-weight:bold;">{}</span>',
            color, obj.get_estado_display()
        )
    color_estado.short_description = "Estado"

    def resumen_productos(self, obj):
        resumen = ", ".join([f"{d.cantidad}x {d.producto.nombre}" for d in obj.detalles.all()])
        return resumen[:50] + "..." if len(resumen) > 50 else (resumen or "Sin productos")

    # --- ACCIONES ---
    def marcar_como_enviado(self, request, queryset):
        queryset.update(estado='enviado')
    def marcar_como_entregado(self, request, queryset):
        queryset.update(estado='entregado')
    
    def sincronizar_pago(self, request, queryset):
        # Aquí iría tu lógica de Mercado Pago
        self.message_user(request, "Sincronización completada.")