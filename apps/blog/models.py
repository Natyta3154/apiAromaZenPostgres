from django.db import models
from django.utils.text import slugify

class Articulo(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título del Artículo")
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    contenido = models.TextField(verbose_name="Contenido")
    imagen_portada = models.URLField(blank=True, null=True, verbose_name="URL de Imagen de Portada")
    fecha_publicacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Publicación")
    actualizado = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True, verbose_name="Visible en el Blog")

    class Meta:
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"
        ordering = ['-fecha_publicacion']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo
