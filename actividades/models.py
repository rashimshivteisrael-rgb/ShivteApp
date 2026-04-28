from django.db import models
from kbutzot.models import Kbutza
from usuarios.models import UsuarioCamp


class PictureDayPedido(models.Model):
    kbutza = models.ForeignKey(Kbutza, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.kbutza.nombre} - {self.titulo}"


class PictureDayFoto(models.Model):
    pedido = models.ForeignKey(PictureDayPedido, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='picture_day/')
    subido_por = models.ForeignKey(
        UsuarioCamp,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.pedido.titulo}"