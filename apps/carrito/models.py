from django.db import models
from django.conf import settings
from apps.productos.models import Producto

class Carrito(models.Model):
    """
    Representa el carrito de compras de un usuario.
    Cada usuario tiene u único carrito vinculado (OneToOneField).
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="carrito",
        verbose_name="Usuario"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Carrito"
        verbose_name_plural = "Carritos"

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

    @property
    def total(self):
        """
        Suma el subtotal de todos los productos que el usuario agregó al carrito.
        Si necesitas agregar costos fijos (ej: envío), se podría modificar aquí.
        """
        return sum(item.subtotal for item in self.items.all())

class ItemCarrito(models.Model):
    """
    Representa un producto específico dentro del carrito con su cantidad.
    """
    carrito = models.ForeignKey(
        Carrito, 
        on_delete=models.CASCADE, 
        related_name="items",
        verbose_name="Carrito"
    )
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE,
        verbose_name="Producto"
    )
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")

    class Meta:
        verbose_name = "Ítem de Carrito"
        verbose_name_plural = "Ítems de Carritos"

    @property
    def subtotal(self):
        """
        Calcula el costo parcial (Precio del Producto x Cantidad).
        Si hubiera descuentos por volumen, aquí es donde se aplicaría la lógica.
        """
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
