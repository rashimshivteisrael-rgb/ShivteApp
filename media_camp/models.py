from django.db import models
from usuarios.models import UsuarioCamp


class FotoCamp(models.Model):
    titulo = models.CharField(max_length=150, blank=True, null=True)
    archivo = models.FileField(upload_to='media_camp/', blank=True, null=True)
    tipo = models.CharField(max_length=20, default='foto')
    subido_por = models.ForeignKey(
        UsuarioCamp,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo if self.titulo else f"Archivo {self.id}"