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
    descripcion = models.TextField(blank=True, null=True)
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
    
class ShevetBankSubasta(models.Model):
    premio = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=False)
    precio_actual = models.IntegerField(default=0)
    kbutza_ganando = models.ForeignKey(
        Kbutza,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    termina_en = models.DateTimeField(null=True, blank=True)
    duracion_minutos = models.IntegerField(default=5)
    iniciada = models.BooleanField(default=False)
    cobrada = models.BooleanField(default=False)
    imagen = models.ImageField(upload_to='subastas/', blank=True, null=True)

    def __str__(self):
        return self.premio


class ShevetBankPuja(models.Model):
    subasta = models.ForeignKey(ShevetBankSubasta, on_delete=models.CASCADE)
    kbutza = models.ForeignKey(Kbutza, on_delete=models.CASCADE)
    madrij = models.ForeignKey(UsuarioCamp, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.kbutza.nombre} - ${self.cantidad}"
    
class ActividadEstado(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    abierta = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} - {'Abierta' if self.abierta else 'Cerrada'}"