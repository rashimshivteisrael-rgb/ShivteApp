from django.db import models
from usuarios.models import UsuarioCamp
from kbutzot.models import Janij


class Camion(models.Model):
    TIPOS = [
        ('ida', 'Ida'),
        ('regreso', 'Regreso'),
    ]

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('saliendo', 'Saliendo'),
        ('en_camino', 'En camino'),
        ('llegando', 'Llegando'),
        ('llego', 'Llegó'),
    ]

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    encargado = models.ForeignKey(
        UsuarioCamp,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'tipo': 'madrij'},
        related_name='camiones_encargado'
    )
    hora_salida = models.CharField(max_length=20, blank=True, null=True)
    hora_estimada = models.CharField(max_length=20, blank=True, null=True)
    link_ruta = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


class CamionMadrij(models.Model):
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    madrij = models.ForeignKey(
        UsuarioCamp,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo': 'madrij'}
    )

class CamionJanij(models.Model):
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    janij = models.ForeignKey(Janij, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.camion.nombre} - {self.janij.nombre}"

    def __str__(self):
        return f"{self.camion.nombre} - {self.madrij.nombre}"

    def __str__(self):
        return f"{self.camion.nombre} - {self.kbutza.nombre}"
    
class AsistenciaCamion(models.Model):
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    janij = models.ForeignKey(Janij, on_delete=models.CASCADE)
    presente = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.camion.nombre} - {self.janij.nombre} - {'Presente' if self.presente else 'Ausente'}"
    
class AsistenciaMadrijCamion(models.Model):
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    madrij = models.ForeignKey(
        UsuarioCamp,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo': 'madrij'}
    )
    presente = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.camion.nombre} - {self.madrij.nombre} - {'Presente' if self.presente else 'Ausente'}"