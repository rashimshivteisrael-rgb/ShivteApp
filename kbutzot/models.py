from django.db import models
from usuarios.models import UsuarioCamp


class Kbutza(models.Model):
    nombre = models.CharField(max_length=100)
    color = models.CharField(max_length=50, blank=True, null=True)
    cuarto = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Janij(models.Model):
    nombre = models.CharField(max_length=100)
    kbutza = models.ForeignKey(Kbutza, on_delete=models.SET_NULL, null=True, blank=True)

    nombre_mama = models.CharField(max_length=100, blank=True, null=True)
    tel_mama = models.CharField(max_length=30, blank=True, null=True)

    nombre_papa = models.CharField(max_length=100, blank=True, null=True)
    tel_papa = models.CharField(max_length=30, blank=True, null=True)

    info_medica = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class MadrijKbutza(models.Model):
    usuario = models.ForeignKey(UsuarioCamp, on_delete=models.CASCADE)
    kbutza = models.ForeignKey(Kbutza, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario.nombre} - {self.kbutza.nombre}"