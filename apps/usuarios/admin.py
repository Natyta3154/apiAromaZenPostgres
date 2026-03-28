from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group, Permission
from django.utils.html import format_html
from django.db.models import Sum, Count, Q
from apps.pedidos.models import Orden


# ==============================
# Permission con autocomplete
# ==============================

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    search_fields = ("name", "codename")


# ==============================
# Re-registrar Group correctamente
# ==============================

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


class CustomGroupAdmin(GroupAdmin):
    search_fields = ("name",)


admin.site.register(Group, CustomGroupAdmin)


# ==============================
# Inline de Órdenes optimizado
# ==============================

class OrdenInline(admin.TabularInline):
    model = Orden
    extra = 0
    fields = ('id', 'fecha_creacion', 'total_formateado', 'estado')
    readonly_fields = ('id', 'fecha_creacion', 'total_formateado', 'estado')
    can_delete = False
    show_change_link = True
    verbose_name = "Historial de Pedido"
    verbose_name_plural = "Historial de Pedidos"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()

    def total_formateado(self, obj):
        try:
            val = float(obj.total or 0)
            return f"${val:,.2f}"
        except:
            return f"${obj.total}"

    total_formateado.short_description = "Total"


# ==================================
# Custom User Admin optimizado
# ==================================

class CustomUserAdmin(BaseUserAdmin):
    inlines = (OrdenInline,)

    list_display = (
        'username',
        'email',
        'get_full_name',
        'is_staff',
        'cantidad_pedidos',
        'total_gastado_badge'
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            total_pagado=Sum(
                'ordenes__total',
                filter=Q(ordenes__estado='pagado')
            ),
            pedidos_count=Count('ordenes')
        )
        return qs

    def cantidad_pedidos(self, obj):
        return obj.pedidos_count or 0

    cantidad_pedidos.short_description = "Pedidos"

    def total_gastado_badge(self, obj):
        total = obj.total_pagado or 0

        try:
            total_str = f"{float(total):,.2f}"
        except:
            total_str = str(total)

        color = "#28a745" if total > 0 else "#6c757d"

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold;">$ {}</span>',
            color,
            total_str
        )

    total_gastado_badge.short_description = "LTV (Gasto Total)"

    def get_fieldsets(self, request, obj=None):
        return (
            ("Cuenta", {
                "fields": ("username", "password"),
            }),
            ("Personal", {
                "fields": ("first_name", "last_name", "email"),
            }),
            ("Permisos", {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions"
                ),
            }),
            ("Trazabilidad", {
                "fields": ("last_login", "date_joined"),
            }),
        )

    autocomplete_fields = ["groups", "user_permissions"]


# ==================================
# Re-registrar User
# ==================================

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)