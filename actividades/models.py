from django.db import models
from kbutzot.models import Kbutza, Janij
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
    
class ShevetBankEstacion(models.Model):
    nombre = models.CharField(max_length=100)
    encargado = models.ForeignKey(
        UsuarioCamp,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'tipo': 'madrij'}
    )

    def __str__(self):
        return self.nombre


class ShevetBankCuenta(models.Model):
    janij = models.OneToOneField(Janij, on_delete=models.CASCADE)
    numero_tarjeta = models.CharField(max_length=30, unique=True)
    saldo = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.numero_tarjeta} - {self.janij.nombre}"


class ShevetBankMovimiento(models.Model):
    cuenta = models.ForeignKey(ShevetBankCuenta, on_delete=models.CASCADE)
    estacion = models.ForeignKey(ShevetBankEstacion, on_delete=models.SET_NULL, null=True)
    madrij = models.ForeignKey(UsuarioCamp, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
    nota = models.CharField(max_length=150, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cuenta.janij.nombre} {self.cantidad}"