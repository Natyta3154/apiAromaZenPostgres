from django.contrib import admin
from django.utils.html import format_html
from .models import Reseña, MensajeContacto

@admin.register(Reseña)
class ReseñaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'calificacion', 'destacado_home', 'fecha_creacion')
    list_filter = ('destacado_home', 'calificacion', 'fecha_creacion')
    search_fields = ('usuario__username', 'producto__nombre', 'comentario')
    list_editable = ('destacado_home',)
    actions = ['marcar_como_destacados']

    def marcar_como_destacados(self, request, queryset):
        queryset.update(destacado_home=True)
    marcar_como_destacados.short_description = "Destacar comentarios seleccionados en el Home"


@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'tipo_badge', 'asunto', 'estado_badge', 'fecha_creacion')
    list_filter = ('tipo', 'estado', 'fecha_creacion')
    search_fields = ('nombre', 'email', 'asunto', 'mensaje')
    readonly_fields = ('nombre', 'email', 'tipo', 'asunto', 'mensaje', 'usuario', 'fecha_creacion')
    actions = ['marcar_como_leido', 'marcar_como_respondido']

    fieldsets = (
        ("Remitente", {
            "fields": ("nombre", "email", "usuario")
        }),
        ("Contenido", {
            "fields": ("tipo", "asunto", "mensaje")
        }),
        ("Gestión", {
            "fields": ("estado", "fecha_creacion")
        }),
    )

    def tipo_badge(self, obj):
        colores = {
            'consulta':   '#17a2b8',
            'queja':      '#dc3545',
            'sugerencia': '#28a745',
            'reclamo':    '#fd7e14',
            'otro':       '#6c757d',
        }
        color = colores.get(obj.tipo, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:12px;font-size:12px;">{}</span>',
            color, obj.get_tipo_display()
        )
    tipo_badge.short_description = "Tipo"

    def estado_badge(self, obj):
        colores = {
            'nuevo':      '#007bff',
            'leido':      '#6c757d',
            'respondido': '#28a745',
        }
        color = colores.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:12px;font-size:12px;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = "Estado"

    def marcar_como_leido(self, request, queryset):
        queryset.update(estado='leido')
    marcar_como_leido.short_description = "Marcar seleccionados como Leídos"

    def marcar_como_respondido(self, request, queryset):
        queryset.update(estado='respondido')
    marcar_como_respondido.short_description = "Marcar seleccionados como Respondidos"
