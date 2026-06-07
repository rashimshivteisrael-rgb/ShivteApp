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

    precio = models.IntegerField(default=0)

    es_banco = models.BooleanField(default=False)


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
    
class ShevetBankGrupo(models.Model):
    nombre = models.CharField(max_length=100)
    codigo_oculto = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.nombre


class ShevetBankGrupoMadrij(models.Model):
    grupo = models.ForeignKey(ShevetBankGrupo, on_delete=models.CASCADE)
    madrij = models.ForeignKey(UsuarioCamp, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.grupo.nombre} - {self.madrij.nombre}"


class ShevetBankGrupoJanij(models.Model):
    grupo = models.ForeignKey(ShevetBankGrupo, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(ShevetBankCuenta, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.grupo.nombre} - {self.cuenta.janij.nombre}"


class ShevetBankRondaEstacion(models.Model):
    estacion = models.ForeignKey(ShevetBankEstacion, on_delete=models.CASCADE)
    encargado = models.ForeignKey(UsuarioCamp, on_delete=models.SET_NULL, null=True)
    activa = models.BooleanField(default=True)
    bote = models.IntegerField(default=0)
    ganador = models.ForeignKey(
        ShevetBankCuenta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rondas_ganadas'
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.estacion.nombre} - {self.fecha_inicio}"


class ShevetBankRondaParticipante(models.Model):
    ronda = models.ForeignKey(ShevetBankRondaEstacion, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(ShevetBankCuenta, on_delete=models.CASCADE)
    cobrado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ronda.estacion.nombre} - {self.cuenta.janij.nombre}"
    
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