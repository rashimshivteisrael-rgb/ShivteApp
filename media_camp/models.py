from django.db import models
from usuarios.models import UsuarioCamp


class FotoCamp(models.Model):
    titulo = models.CharField(max_length=150, blank=True, null=True)
    imagen = models.ImageField(upload_to='fotos_camp/')
    subido_por = models.ForeignKey(
        UsuarioCamp,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo if self.titulo else f"Foto {self.id}"