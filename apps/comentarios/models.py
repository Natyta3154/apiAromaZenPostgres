from django.db import models
from django.conf import settings
from apps.productos.models import Producto
from django.core.validators import MinValueValidator, MaxValueValidator

class Reseña(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="reseñas",
        verbose_name="Cliente"
    )
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE, 
        related_name="reseñas",
        verbose_name="Producto"
    )
    comentario = models.TextField(verbose_name="Comentario")
    calificacion = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Calificación (1-5)"
    )
    destacado_home = models.BooleanField(
        default=False, 
        verbose_name="Mostrar en el Home (Destacado)"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Reseña de Cliente"
        verbose_name_plural = "Reseñas de Clientes"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Reseña de {self.usuario.username} sobre {self.producto.nombre}"


class MensajeContacto(models.Model):
    """
    Modelo para los mensajes de contacto que llegan al administrador.
    """
    TIPO_CHOICES = [
        ('consulta', '❓ Consulta General'),
        ('queja', '😤 Queja'),
        ('sugerencia', '💡 Sugerencia'),
        ('reclamo', '📢 Reclamo'),
        ('otro', '📝 Otro'),
    ]

    ESTADO_CHOICES = [
        ('nuevo', '🔵 Nuevo'),
        ('leido', '👁️ Leído'),
        ('respondido', '✅ Respondido'),
    ]

    nombre = models.CharField(max_length=120, verbose_name="Nombre Completo")
    email = models.EmailField(verbose_name="Email de Contacto")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='consulta', verbose_name="Tipo de Mensaje")
    asunto = models.CharField(max_length=200, verbose_name="Asunto")
    mensaje = models.TextField(verbose_name="Mensaje")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='nuevo', verbose_name="Estado")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mensajes_contacto",
        verbose_name="Usuario (si está logueado)"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Envío")

    class Meta:
        verbose_name = "Mensaje de Contacto"
        verbose_name_plural = "Mensajes de Contacto"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.asunto} — {self.nombre}"
