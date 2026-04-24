from django.db import models


class HorarioCamp(models.Model):
    dia = models.CharField(max_length=100)
    hora = models.CharField(max_length=20)
    actividad = models.CharField(max_length=200)
    lugar = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.dia} - {self.hora} - {self.actividad}"