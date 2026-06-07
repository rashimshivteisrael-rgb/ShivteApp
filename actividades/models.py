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
       
 
class ActividadEstado(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    abierta = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} - {'Abierta' if self.abierta else 'Cerrada'}"
    
class ShivteGotTalentRol(models.Model):
    usuario = models.ForeignKey(UsuarioCamp, on_delete=models.CASCADE)
    rol = models.CharField(max_length=30)  # inscripciones / juez

    def __str__(self):
        return f"{self.usuario.nombre} - {self.rol}"


class ShivteGotTalentConcursante(models.Model):
    janij = models.ForeignKey(Janij, on_delete=models.CASCADE)
    talento = models.CharField(max_length=150)
    activo = models.BooleanField(default=False)
    terminado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.janij.nombre} - {self.talento}"


class ShivteGotTalentCalificacion(models.Model):
    concursante = models.ForeignKey(ShivteGotTalentConcursante, on_delete=models.CASCADE)
    juez = models.ForeignKey(UsuarioCamp, on_delete=models.CASCADE)

    originalidad = models.IntegerField()
    ejecucion = models.IntegerField()
    general = models.IntegerField()

    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('concursante', 'juez')

    def total(self):
        return self.originalidad + self.ejecucion + self.general

    def __str__(self):
        return f"{self.concursante} - {self.juez.nombre}"
    
class ShivteTVPedido(models.Model):
    kbutza = models.ForeignKey(Kbutza, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.kbutza.nombre} - {self.titulo}"


class ShivteTVVideo(models.Model):
    pedido = models.OneToOneField(ShivteTVPedido, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='shivte_tv/')
    subido_por = models.ForeignKey(
        UsuarioCamp,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video {self.pedido.kbutza.nombre}"