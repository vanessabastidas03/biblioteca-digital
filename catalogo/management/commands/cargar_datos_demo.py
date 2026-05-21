"""
Comando: python manage.py cargar_datos_demo
Crea datos de prueba sin duplicar registros existentes.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date


class Command(BaseCommand):
    help = 'Carga datos de prueba: categorías, autores, libros, usuarios, préstamos y reservas.'

    def handle(self, *args, **options):
        # Importaciones locales para evitar errores de app no lista
        from catalogo.models import Categoria, Autor, Libro
        from prestamos.models import Prestamo, Reserva
        from accounts.models import Usuario

        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Cargando datos de demostración ===\n'))

        # ── Categorías ──────────────────────────────────────────────
        categorias_data = [
            {'nombre': 'Ficción', 'color': '#A7C7E7', 'descripcion': 'Novelas y cuentos de ficción literaria.'},
            {'nombre': 'Ciencia y Tecnología', 'color': '#B8E0D2', 'descripcion': 'Libros de ciencias exactas y tecnología.'},
            {'nombre': 'Historia', 'color': '#CDB4DB', 'descripcion': 'Historia universal y latinoamericana.'},
            {'nombre': 'Filosofía', 'color': '#FFC8DD', 'descripcion': 'Pensamiento filosófico clásico y contemporáneo.'},
            {'nombre': 'Programación', 'color': '#BDE0FE', 'descripcion': 'Libros de desarrollo de software y algoritmos.'},
        ]
        categorias = {}
        for d in categorias_data:
            obj, created = Categoria.objects.get_or_create(
                nombre=d['nombre'],
                defaults={'color': d['color'], 'descripcion': d['descripcion']}
            )
            categorias[d['nombre']] = obj
            status = 'creada' if created else 'ya existía'
            self.stdout.write(f'  Categoría "{obj.nombre}" — {status}')

        # ── Autores ─────────────────────────────────────────────────
        autores_data = [
            {'nombre': 'Gabriel', 'apellido': 'García Márquez', 'nacionalidad': 'Colombia'},
            {'nombre': 'Isaac',   'apellido': 'Asimov',         'nacionalidad': 'Estados Unidos'},
            {'nombre': 'Yuval',   'apellido': 'Noah Harari',    'nacionalidad': 'Israel'},
            {'nombre': 'Plato',   'apellido': '',               'nacionalidad': 'Grecia'},
            {'nombre': 'Robert',  'apellido': 'Martin',         'nacionalidad': 'Estados Unidos'},
            {'nombre': 'Isabel',  'apellido': 'Allende',        'nacionalidad': 'Chile'},
            {'nombre': 'Stephen', 'apellido': 'Hawking',        'nacionalidad': 'Reino Unido'},
        ]
        autores = {}
        for d in autores_data:
            obj, created = Autor.objects.get_or_create(
                nombre=d['nombre'], apellido=d['apellido'],
                defaults={'nacionalidad': d['nacionalidad']}
            )
            autores[f"{d['nombre']} {d['apellido']}".strip()] = obj
            status = 'creado' if created else 'ya existía'
            self.stdout.write(f'  Autor "{obj}" — {status}')

        # ── Libros ──────────────────────────────────────────────────
        hoy = date.today()
        libros_data = [
            {
                'titulo': 'Cien años de soledad',
                'isbn': '978-84-376-0494-7',
                'editorial': 'Editorial Sudamericana',
                'anio_publicacion': 1967,
                'estado': Libro.ESTADO_DISPONIBLE,
                'tipo': Libro.TIPO_FISICO,
                'cantidad_ejemplares': 3,
                'ejemplares_disponibles': 3,
                'descripcion': 'Obra maestra del realismo mágico latinoamericano.',
                'autores_keys': ['Gabriel García Márquez'],
                'categorias_keys': ['Ficción'],
            },
            {
                'titulo': 'Fundación',
                'isbn': '978-0-553-29335-7',
                'editorial': 'Gnome Press',
                'anio_publicacion': 1951,
                'estado': Libro.ESTADO_PRESTADO,
                'tipo': Libro.TIPO_FISICO,
                'cantidad_ejemplares': 2,
                'ejemplares_disponibles': 0,
                'descripcion': 'La saga espacial más influyente de la ciencia ficción.',
                'autores_keys': ['Isaac Asimov'],
                'categorias_keys': ['Ficción', 'Ciencia y Tecnología'],
            },
            {
                'titulo': 'Sapiens: De animales a dioses',
                'isbn': '978-84-9992-388-0',
                'editorial': 'Debate',
                'anio_publicacion': 2011,
                'estado': Libro.ESTADO_DISPONIBLE,
                'tipo': Libro.TIPO_FISICO,
                'cantidad_ejemplares': 4,
                'ejemplares_disponibles': 3,
                'descripcion': 'Historia breve de la humanidad.',
                'autores_keys': ['Yuval Noah Harari'],
                'categorias_keys': ['Historia'],
            },
            {
                'titulo': 'La República',
                'isbn': '978-84-249-2118-2',
                'editorial': 'Gredos',
                'anio_publicacion': -380,
                'estado': Libro.ESTADO_DISPONIBLE,
                'tipo': Libro.TIPO_FISICO,
                'cantidad_ejemplares': 2,
                'ejemplares_disponibles': 2,
                'descripcion': 'Diálogo filosófico clásico sobre justicia y política.',
                'autores_keys': ['Plato'],
                'categorias_keys': ['Filosofía'],
            },
            {
                'titulo': 'Código Limpio',
                'isbn': '978-0-13-235088-4',
                'editorial': 'Prentice Hall',
                'anio_publicacion': 2008,
                'estado': Libro.ESTADO_PRESTADO,
                'tipo': Libro.TIPO_FISICO,
                'cantidad_ejemplares': 3,
                'ejemplares_disponibles': 0,
                'descripcion': 'Manual de artesanía del software ágil.',
                'autores_keys': ['Robert Martin'],
                'categorias_keys': ['Programación'],
            },
            {
                'titulo': 'La casa de los espíritus',
                'isbn': '978-84-9759-214-5',
                'editorial': 'Plaza & Janés',
                'anio_publicacion': 1982,
                'estado': Libro.ESTADO_DISPONIBLE,
                'tipo': Libro.TIPO_FISICO,
                'cantidad_ejemplares': 2,
                'ejemplares_disponibles': 2,
                'descripcion': 'Novela épica chilena con elementos de realismo mágico.',
                'autores_keys': ['Isabel Allende'],
                'categorias_keys': ['Ficción', 'Historia'],
            },
            {
                'titulo': 'Historia del tiempo',
                'isbn': '978-84-226-2011-9',
                'editorial': 'Crítica',
                'anio_publicacion': 1988,
                'estado': Libro.ESTADO_RESERVADO,
                'tipo': Libro.TIPO_FISICO,
                'cantidad_ejemplares': 2,
                'ejemplares_disponibles': 1,
                'descripcion': 'Del big bang a los agujeros negros.',
                'autores_keys': ['Stephen Hawking'],
                'categorias_keys': ['Ciencia y Tecnología'],
            },
            {
                'titulo': 'El universo en una cáscara de nuez',
                'isbn': '978-84-08-03685-9',
                'editorial': 'Crítica',
                'anio_publicacion': 2001,
                'estado': Libro.ESTADO_DISPONIBLE,
                'tipo': Libro.TIPO_DIGITAL,
                'cantidad_ejemplares': 5,
                'ejemplares_disponibles': 5,
                'descripcion': 'Viaje ilustrado por el cosmos cuántico.',
                'autores_keys': ['Stephen Hawking'],
                'categorias_keys': ['Ciencia y Tecnología'],
            },
            {
                'titulo': 'Patrones de diseño',
                'isbn': '978-0-201-63361-0',
                'editorial': 'Addison-Wesley',
                'anio_publicacion': 1994,
                'estado': Libro.ESTADO_DISPONIBLE,
                'tipo': Libro.TIPO_FISICO,
                'cantidad_ejemplares': 2,
                'ejemplares_disponibles': 2,
                'descripcion': 'Elementos de software orientado a objetos reutilizable.',
                'autores_keys': ['Robert Martin'],
                'categorias_keys': ['Programación'],
            },
            {
                'titulo': 'Homo Deus',
                'isbn': '978-84-9992-784-0',
                'editorial': 'Debate',
                'anio_publicacion': 2015,
                'estado': Libro.ESTADO_DISPONIBLE,
                'tipo': Libro.TIPO_FISICO,
                'cantidad_ejemplares': 3,
                'ejemplares_disponibles': 3,
                'descripcion': 'Breve historia del mañana.',
                'autores_keys': ['Yuval Noah Harari'],
                'categorias_keys': ['Historia', 'Filosofía'],
            },
        ]

        libros = {}
        for d in libros_data:
            obj, created = Libro.objects.get_or_create(
                isbn=d['isbn'],
                defaults={
                    'titulo': d['titulo'],
                    'editorial': d.get('editorial', ''),
                    'anio_publicacion': d.get('anio_publicacion'),
                    'estado': d['estado'],
                    'tipo': d['tipo'],
                    'cantidad_ejemplares': d['cantidad_ejemplares'],
                    'ejemplares_disponibles': d['ejemplares_disponibles'],
                    'descripcion': d.get('descripcion', ''),
                }
            )
            if created:
                for ak in d['autores_keys']:
                    if ak in autores:
                        obj.autores.add(autores[ak])
                for ck in d['categorias_keys']:
                    if ck in categorias:
                        obj.categorias.add(categorias[ck])
            libros[d['isbn']] = obj
            status = 'creado' if created else 'ya existía'
            self.stdout.write(f'  Libro "{obj.titulo[:40]}" — {status}')

        # ── Usuarios ────────────────────────────────────────────────
        usuarios = {}

        bib, created = Usuario.objects.get_or_create(
            username='admin_bib',
            defaults={
                'first_name': 'Ana',
                'last_name': 'Bibliotecaria',
                'email': 'admin@biblioteca.co',
                'rol': Usuario.ROL_BIBLIOTECARIO,
                'is_staff': True,
            }
        )
        if created:
            bib.set_password('Admin1234!')
            bib.save()
        usuarios['bib'] = bib
        self.stdout.write(f'  Usuario bibliotecario "admin_bib" — {"creado" if created else "ya existía"}')

        for uname, fname, lname in [('lector_juan', 'Juan', 'Pérez'), ('lector_sofia', 'Sofía', 'Ramírez')]:
            user, created = Usuario.objects.get_or_create(
                username=uname,
                defaults={
                    'first_name': fname, 'last_name': lname,
                    'email': f'{uname}@biblioteca.co',
                    'rol': Usuario.ROL_LECTOR,
                }
            )
            if created:
                user.set_password('Lector1234!')
                user.save()
            usuarios[uname] = user
            self.stdout.write(f'  Usuario lector "{uname}" — {"creado" if created else "ya existía"}')

        # ── Préstamos ───────────────────────────────────────────────
        libro_fundacion = libros.get('978-0-553-29335-7')
        libro_codigo    = libros.get('978-0-201-63361-0')  # Código limpio → isbn incorrecto, ajustado abajo
        libro_codigo    = libros.get('978-0-13-235088-4')

        lector1 = usuarios.get('lector_juan')
        lector2 = usuarios.get('lector_sofia')

        # Préstamo activo (vence en 7 días)
        if libro_fundacion and lector1:
            _, created = Prestamo.objects.get_or_create(
                libro=libro_fundacion,
                usuario=lector1,
                estado=Prestamo.ESTADO_ACTIVO,
                defaults={
                    'fecha_vencimiento': hoy + timedelta(days=7),
                }
            )
            self.stdout.write(f'  Préstamo activo (Fundación → lector_juan) — {"creado" if created else "ya existía"}')

        # Préstamo activo para Código Limpio
        if libro_codigo and lector2:
            _, created = Prestamo.objects.get_or_create(
                libro=libro_codigo,
                usuario=lector2,
                estado=Prestamo.ESTADO_ACTIVO,
                defaults={
                    'fecha_vencimiento': hoy + timedelta(days=3),
                }
            )
            self.stdout.write(f'  Préstamo activo (Código Limpio → lector_sofia) — {"creado" if created else "ya existía"}')

        # Préstamo devuelto (histórico)
        libro_sapiens = libros.get('978-84-9992-388-0')
        if libro_sapiens and lector1:
            _, created = Prestamo.objects.get_or_create(
                libro=libro_sapiens,
                usuario=lector1,
                estado=Prestamo.ESTADO_DEVUELTO,
                defaults={
                    'fecha_vencimiento': hoy - timedelta(days=10),
                    'fecha_devolucion': timezone.now() - timedelta(days=12),
                }
            )
            self.stdout.write(f'  Préstamo devuelto (Sapiens → lector_juan) — {"creado" if created else "ya existía"}')

        # Préstamo retrasado (vencido hace 5 días)
        libro_cien = libros.get('978-84-376-0494-7')
        if libro_cien and lector2:
            p_retrasado, created = Prestamo.objects.get_or_create(
                libro=libro_cien,
                usuario=lector2,
                estado__in=[Prestamo.ESTADO_RETRASADO, Prestamo.ESTADO_ACTIVO],
                defaults={
                    'fecha_vencimiento': hoy - timedelta(days=5),
                    'estado': Prestamo.ESTADO_RETRASADO,
                    'dias_retraso': 5,
                }
            )
            if created:
                # Actualizar ejemplares del libro
                libro_cien.ejemplares_disponibles = max(0, libro_cien.ejemplares_disponibles - 1)
                libro_cien.save()
            self.stdout.write(f'  Préstamo retrasado (100 años → lector_sofia) — {"creado" if created else "ya existía"}')

        # ── Reservas ────────────────────────────────────────────────
        libro_historia = libros.get('978-84-9992-784-0')  # Homo Deus
        if libro_historia and lector1:
            _, created = Reserva.objects.get_or_create(
                libro=libro_historia,
                usuario=lector1,
                estado=Reserva.ESTADO_PENDIENTE,
                defaults={
                    'fecha_expiracion': hoy + timedelta(days=3),
                }
            )
            self.stdout.write(f'  Reserva pendiente (Homo Deus → lector_juan) — {"creado" if created else "ya existía"}')

        libro_hawking = libros.get('978-84-9992-388-0')  # Historia del Tiempo
        libro_hawking = libros.get('978-84-226-2011-9')
        if libro_hawking and lector2:
            _, created = Reserva.objects.get_or_create(
                libro=libro_hawking,
                usuario=lector2,
                estado=Reserva.ESTADO_PENDIENTE,
                defaults={
                    'fecha_expiracion': hoy + timedelta(days=2),
                }
            )
            self.stdout.write(f'  Reserva pendiente (Historia del Tiempo → lector_sofia) — {"creado" if created else "ya existía"}')

        self.stdout.write(self.style.SUCCESS('\n✓ Datos de demostración cargados correctamente.\n'))
        self.stdout.write(self.style.WARNING('Usuarios de prueba:'))
        self.stdout.write('  Bibliotecario: admin_bib / Admin1234!')
        self.stdout.write('  Lector 1:      lector_juan / Lector1234!')
        self.stdout.write('  Lector 2:      lector_sofia / Lector1234!\n')
