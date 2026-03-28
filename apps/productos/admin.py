from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Producto

class ProductoAdminForm(forms.ModelForm):
    # Definimos el campo de incremento explícitamente
    agregar_stock = forms.IntegerField(
        label="Nuevas Unidades a Ingresar",
        required=False,
        initial=0,
        help_text="⚠️ Suma al Stock Disponible y al Total Histórico al Guardar."
    )

    class Meta:
        model = Producto
        # Incluimos los campos del modelo y el campo personalizado
        fields = [
            'nombre', 'descripcion', 'categoria', 'precio', 
            'stock', 'stock_total_historico', 'imagen_url', 
            'activo', 'destacado', 'agregar_stock'
        ]

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    form = ProductoAdminForm
    list_display = ('nombre_con_imagen', 'categoria', 'precio_formateado', 'stock_display', 'activo', 'destacado','stock_total_historico','stock')
    list_filter = ('activo', 'destacado', 'categoria')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo', 'destacado')
    
    def get_fieldsets(self, request, obj=None):
        if not obj:  # Creación
            return (
                ('General', {
                    'fields': (('nombre', 'categoria'), 'descripcion', 'precio', 'stock', 'imagen_url')
                }),
                ('Visibilidad', {
                    'fields': ('activo', 'destacado'),
                }),
            )
        # Edición
        return (
            ('General', {
                'fields': (('nombre', 'categoria'), 'descripcion', 'precio', 'imagen_url')
            }),
            ('Inventario', {
                'fields': ('stock', 'agregar_stock', 'stock_total_historico'),
                'description': "Gestión de stock actual e histórico."
            }),
            ('Visibilidad', {
                'fields': ('activo', 'destacado'),
            }),
        )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Edición
            return ('stock', 'stock_total_historico')
        # Creación
        return ('stock_total_historico',)

    def nombre_con_imagen(self, obj):
        if obj.imagen_url:
            return format_html(
                '<img src="{}" style="width: 30px; height: 30px; border-radius: 5px; margin-right: 10px; vertical-align: middle;">'
                '<span>{}</span>',
                obj.imagen_url, obj.nombre
            )
        return format_html('<span style="margin-left: 40px;">{}</span>', obj.nombre)
    nombre_con_imagen.short_description = "Producto"

    def precio_formateado(self, obj):
        try:
            val = float(obj.precio or 0)
            return f"${val:,.2f}"
        except:
            return f"${obj.precio}"
    precio_formateado.short_description = "Precio"

    def stock_display(self, obj):
        color = "#28a745" if obj.stock > 10 else "#dc3545"
        return format_html(
            '<b style="color: {};">{} unidades</b>',
            color, obj.stock
        )
    stock_display.short_description = "Stock"


    def save_model(self, request, obj, form, change):
        agregar = form.cleaned_data.get('agregar_stock') or 0
        if agregar > 0:
            obj.stock += agregar
            obj.stock_total_historico += agregar
        
        if not change:
            obj.stock_total_historico = obj.stock

        super().save_model(request, obj, form, change)
