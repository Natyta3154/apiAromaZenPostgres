from django.contrib import admin
from .models import Carrito, ItemCarrito

class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'total', 'fecha_creacion', 'ultima_actualizacion')
    inlines = [ItemCarritoInline]
    
    fieldsets = (
        ('🛒 Resumen del Carrito', {
            'fields': ('usuario', 'total')
        }),
        ('🕒 Trazabilidad', {
            'fields': ('fecha_creacion', 'ultima_actualizacion'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('total', 'fecha_creacion', 'ultima_actualizacion')

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ('carrito', 'producto', 'cantidad', 'subtotal')

# Register your models here.
