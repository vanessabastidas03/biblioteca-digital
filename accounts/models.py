from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Usuario personalizado que extiende el usuario de Django.
    Roles: LECTOR (usuario normal) o BIBLIOTECARIO (administrador).
    """
    ROL_LECTOR = 'lector'
    ROL_BIBLIOTECARIO = 'bibliotecario'

    ROLES = [
        (ROL_LECTOR, 'Lector'),
        (ROL_BIBLIOTECARIO, 'Bibliotecario'),
    ]

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default=ROL_LECTOR,
        verbose_name='Rol'
    )
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    direccion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Dirección'
    )
    foto_perfil = models.ImageField(
        upload_to='perfiles/',
        blank=True,
        null=True,
        verbose_name='Foto de perfil'
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )
    sancionado = models.BooleanField(
        default=False,
        verbose_name='Sancionado'
    )
    fecha_fin_sancion = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fin de sanción'
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"

    @property
    def es_bibliotecario(self):
        return self.rol == self.ROL_BIBLIOTECARIO

    @property
    def es_lector(self):
        return self.rol == self.ROL_LECTOR