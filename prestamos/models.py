from django.db import models
from django.conf import settings
from django.utils import timezone
from catalogo.models import Libro


class Reserva(models.Model):
    """Reserva de un libro (antes del préstamo físico)."""

    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_CONFIRMADA = 'confirmada'
    ESTADO_CANCELADA = 'cancelada'
    ESTADO_EXPIRADA = 'expirada'

    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_CONFIRMADA, 'Confirmada'),
        (ESTADO_CANCELADA, 'Cancelada'),
        (ESTADO_EXPIRADA, 'Expirada'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name='Usuario'
    )
    libro = models.ForeignKey(
        Libro,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name='Libro'
    )
    fecha_reserva = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de reserva'
    )
    fecha_expiracion = models.DateField(
        verbose_name='Fecha de expiración'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_PENDIENTE,
        verbose_name='Estado'
    )
    notas = models.TextField(
        blank=True,
        verbose_name='Notas'
    )

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha_reserva']

    def __str__(self):
        return f"Reserva de {self.usuario} — {self.libro}"

    def esta_vencida(self):
        return (
            self.estado == self.ESTADO_PENDIENTE and
            self.fecha_expiracion < timezone.now().date()
        )


class Prestamo(models.Model):
    """Préstamo activo de un libro a un usuario."""

    ESTADO_ACTIVO = 'activo'
    ESTADO_DEVUELTO = 'devuelto'
    ESTADO_RETRASADO = 'retrasado'
    ESTADO_RENOVADO = 'renovado'

    ESTADOS = [
        (ESTADO_ACTIVO, 'Activo'),
        (ESTADO_DEVUELTO, 'Devuelto'),
        (ESTADO_RETRASADO, 'Retrasado'),
        (ESTADO_RENOVADO, 'Renovado'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prestamos',
        verbose_name='Usuario'
    )
    libro = models.ForeignKey(
        Libro,
        on_delete=models.CASCADE,
        related_name='prestamos',
        verbose_name='Libro'
    )
    reserva = models.OneToOneField(
        Reserva,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prestamo',
        verbose_name='Reserva origen'
    )
    fecha_prestamo = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de préstamo'
    )
    fecha_vencimiento = models.DateField(
        verbose_name='Fecha de vencimiento'
    )
    fecha_devolucion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de devolución'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_ACTIVO,
        verbose_name='Estado'
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    dias_retraso = models.IntegerField(
        default=0,
        verbose_name='Días de retraso'
    )

    class Meta:
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'
        ordering = ['-fecha_prestamo']

    def __str__(self):
        return f"Préstamo de {self.usuario} — {self.libro}"

    @property
    def esta_retrasado(self):
        if self.estado == self.ESTADO_ACTIVO:
            return timezone.now().date() > self.fecha_vencimiento
        return False

    @property
    def calcular_dias_retraso(self):
        if self.esta_retrasado:
            delta = timezone.now().date() - self.fecha_vencimiento
            return delta.days
        return 0


class Sancion(models.Model):
    """Sanción aplicada a un usuario por retraso en devolución."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sanciones',
        verbose_name='Usuario'
    )
    prestamo = models.OneToOneField(
        Prestamo,
        on_delete=models.CASCADE,
        related_name='sancion',
        verbose_name='Préstamo'
    )
    fecha_inicio = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha de inicio'
    )
    fecha_fin = models.DateField(
        verbose_name='Fecha de fin'
    )
    dias_sancion = models.IntegerField(
        verbose_name='Días de sanción'
    )
    motivo = models.TextField(
        verbose_name='Motivo'
    )
    activa = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )

    class Meta:
        verbose_name = 'Sanción'
        verbose_name_plural = 'Sanciones'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"Sanción de {self.usuario} — {self.dias_sancion} días"