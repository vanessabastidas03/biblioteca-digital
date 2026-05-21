from django.db import models


class Categoria(models.Model):
    """Categorías de libros: Ficción, Ciencia, Historia, etc."""
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre'
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    color = models.CharField(
        max_length=7,
        default='#6c757d',
        help_text='Color en formato HEX, ej: #FF5733',
        verbose_name='Color'
    )

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Autor(models.Model):
    """Autores de los libros."""
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    apellido = models.CharField(
        max_length=100,
        verbose_name='Apellido'
    )
    biografia = models.TextField(
        blank=True,
        verbose_name='Biografía'
    )
    nacionalidad = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Nacionalidad'
    )
    foto = models.ImageField(
        upload_to='autores/',
        blank=True,
        null=True,
        verbose_name='Foto'
    )

    class Meta:
        verbose_name = 'Autor'
        verbose_name_plural = 'Autores'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


class Libro(models.Model):
    """Modelo principal: representa un libro en la biblioteca."""

    ESTADO_DISPONIBLE = 'disponible'
    ESTADO_PRESTADO = 'prestado'
    ESTADO_RESERVADO = 'reservado'
    ESTADO_MANTENIMIENTO = 'mantenimiento'

    ESTADOS = [
        (ESTADO_DISPONIBLE, 'Disponible'),
        (ESTADO_PRESTADO, 'Prestado'),
        (ESTADO_RESERVADO, 'Reservado'),
        (ESTADO_MANTENIMIENTO, 'En mantenimiento'),
    ]

    TIPO_FISICO = 'fisico'
    TIPO_DIGITAL = 'digital'

    TIPOS = [
        (TIPO_FISICO, 'Físico'),
        (TIPO_DIGITAL, 'Digital'),
    ]

    titulo = models.CharField(
        max_length=300,
        verbose_name='Título'
    )
    isbn = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='ISBN'
    )
    autores = models.ManyToManyField(
        Autor,
        related_name='libros',
        verbose_name='Autores'
    )
    categorias = models.ManyToManyField(
        Categoria,
        related_name='libros',
        verbose_name='Categorías'
    )
    editorial = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Editorial'
    )
    anio_publicacion = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Año de publicación'
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    portada = models.ImageField(
        upload_to='portadas/',
        blank=True,
        null=True,
        verbose_name='Portada'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_DISPONIBLE,
        verbose_name='Estado'
    )
    tipo = models.CharField(
        max_length=10,
        choices=TIPOS,
        default=TIPO_FISICO,
        verbose_name='Tipo'
    )
    cantidad_ejemplares = models.IntegerField(
        default=1,
        verbose_name='Cantidad de ejemplares'
    )
    ejemplares_disponibles = models.IntegerField(
        default=1,
        verbose_name='Ejemplares disponibles'
    )
    fecha_adquisicion = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha de adquisición'
    )
    ubicacion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Ubicación en biblioteca'
    )

    class Meta:
        verbose_name = 'Libro'
        verbose_name_plural = 'Libros'
        ordering = ['titulo']

    def __str__(self):
        return self.titulo

    @property
    def esta_disponible(self):
        return self.ejemplares_disponibles > 0