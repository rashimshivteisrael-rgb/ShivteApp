from django.db import models


class UsuarioCamp(models.Model):
    TIPOS = [
        ('admin', 'Admin'),
        ('madrij', 'Madrij'),
        ('arbitro', 'Arbitro'),
        ('consulta', 'Consulta'),
    ]

    nombre = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPOS)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"