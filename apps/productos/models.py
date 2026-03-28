from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Categoria(models.Model):
    """
    Clasificación de los productos (ej: Sahumerios, Aceites, Velas).
    """
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Categoría")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    """
    El alma del ecommerce. Contiene precio, stock y descripción.
    """
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    descripcion = models.TextField(verbose_name="Descripción del Producto")
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Precio"
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock Disponible")
    # Este campo sirve para auditoría interna, no se muestra al cliente
    stock_total_historico = models.PositiveIntegerField(default=0, verbose_name="Total Histórico de Stock")
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="productos",
        verbose_name="Categoría"
    )
    imagen_url = models.URLField(blank=True, null=True, verbose_name="URL de la Imagen")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    activo = models.BooleanField(default=True, verbose_name="Está Activo")
    destacado = models.BooleanField(default=False, verbose_name="Producto Destacado")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.nombre

    def tiene_stock(self, cantidad):
        """
        Función de seguridad: Verifica si hay suficientes unidades antes de permitir una compra.
        Si necesitas cambiar la lógica de stock (ej: permitir sobreventa), se hace aquí.
        """
        return self.stock >= cantidad
