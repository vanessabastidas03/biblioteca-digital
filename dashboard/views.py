# dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
import json

from catalogo.models import Libro, Autor, Categoria
from prestamos.models import Prestamo, Reserva, Sancion
from accounts.models import Usuario


@login_required
def index(request):
    """Dashboard principal — solo para bibliotecarios."""
    if not request.user.es_bibliotecario:
        return redirect('dashboard:lector')

    hoy = timezone.now().date()
    hace_30_dias = hoy - timedelta(days=30)

    # ── Estadísticas generales ──
    total_libros = Libro.objects.count()
    total_usuarios = Usuario.objects.filter(rol=Usuario.ROL_LECTOR).count()
    prestamos_activos = Prestamo.objects.filter(estado='activo').count()
    prestamos_retrasados = Prestamo.objects.filter(estado='retrasado').count()
    reservas_pendientes = Reserva.objects.filter(estado='pendiente').count()
    libros_disponibles = Libro.objects.filter(estado='disponible').count()
    sanciones_activas = Sancion.objects.filter(activa=True).count()

    # ── Gráfico 1: Préstamos por mes (últimos 6 meses) ──
    prestamos_por_mes = (
        Prestamo.objects
        .filter(fecha_prestamo__date__gte=hoy - timedelta(days=180))
        .annotate(mes=TruncMonth('fecha_prestamo'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    labels_meses = []
    datos_meses = []
    MESES_ES = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }
    for item in prestamos_por_mes:
        mes = item['mes']
        labels_meses.append(f"{MESES_ES[mes.month]} {mes.year}")
        datos_meses.append(item['total'])

    # ── Gráfico 2: Top 5 libros más prestados ──
    top_libros = (
        Prestamo.objects
        .values('libro__titulo')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )
    labels_libros = [item['libro__titulo'][:25] + '...' if len(item['libro__titulo']) > 25
                     else item['libro__titulo'] for item in top_libros]
    datos_libros = [item['total'] for item in top_libros]

    # ── Gráfico 3: Libros por estado (dona) ──
    estados_libros = (
        Libro.objects
        .values('estado')
        .annotate(total=Count('id'))
        .order_by('estado')
    )
    ESTADO_NOMBRES = {
        'disponible': 'Disponible',
        'prestado': 'Prestado',
        'reservado': 'Reservado',
        'mantenimiento': 'Mantenimiento'
    }
    ESTADO_COLORES = {
        'disponible': '#28a745',
        'prestado': '#fd7e14',
        'reservado': '#007bff',
        'mantenimiento': '#6c757d'
    }
    labels_estados = [ESTADO_NOMBRES.get(e['estado'], e['estado']) for e in estados_libros]
    datos_estados = [e['total'] for e in estados_libros]
    colores_estados = [ESTADO_COLORES.get(e['estado'], '#999') for e in estados_libros]

    # ── Últimos préstamos y reservas ──
    ultimos_prestamos = Prestamo.objects.select_related('usuario', 'libro').order_by('-fecha_prestamo')[:5]
    ultimas_reservas = Reserva.objects.filter(estado='pendiente').select_related('usuario', 'libro')[:5]

    context = {
        # Estadísticas
        'total_libros': total_libros,
        'total_usuarios': total_usuarios,
        'prestamos_activos': prestamos_activos,
        'prestamos_retrasados': prestamos_retrasados,
        'reservas_pendientes': reservas_pendientes,
        'libros_disponibles': libros_disponibles,
        'sanciones_activas': sanciones_activas,
        # Gráficos (JSON para Chart.js)
        'labels_meses': json.dumps(labels_meses),
        'datos_meses': json.dumps(datos_meses),
        'labels_libros': json.dumps(labels_libros),
        'datos_libros': json.dumps(datos_libros),
        'labels_estados': json.dumps(labels_estados),
        'datos_estados': json.dumps(datos_estados),
        'colores_estados': json.dumps(colores_estados),
        # Listas
        'ultimos_prestamos': ultimos_prestamos,
        'ultimas_reservas': ultimas_reservas,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def lector(request):
    """Dashboard personal para lectores."""
    # Si es bibliotecario, va al panel de administración
    if request.user.es_bibliotecario:
        return redirect('dashboard:index')

    hoy = timezone.now().date()
    usuario = request.user

    # ── Estadísticas personales ──
    mis_prestamos = Prestamo.objects.filter(usuario=usuario)
    mis_prestamos_activos    = mis_prestamos.filter(estado='activo').count()
    mis_prestamos_retrasados = mis_prestamos.filter(estado='retrasado').count()
    mis_reservas_pendientes  = Reserva.objects.filter(usuario=usuario, estado='pendiente').count()
    libros_disponibles       = Libro.objects.filter(estado='disponible').count()

    # ── Últimos préstamos propios ──
    ultimos_prestamos = (
        mis_prestamos
        .select_related('libro')
        .order_by('-fecha_prestamo')[:5]
    )

    # ── Reservas propias ──
    mis_reservas = (
        Reserva.objects
        .filter(usuario=usuario)
        .select_related('libro')
        .order_by('-fecha_reserva')[:5]
    )

    # ── Libros disponibles recientes (sugerencias) ──
    libros_recientes = (
        Libro.objects
        .filter(estado='disponible')
        .prefetch_related('autores', 'categorias')
        .order_by('-id')[:5]
    )

    context = {
        'mis_prestamos_activos':    mis_prestamos_activos,
        'mis_prestamos_retrasados': mis_prestamos_retrasados,
        'mis_reservas_pendientes':  mis_reservas_pendientes,
        'libros_disponibles':       libros_disponibles,
        'ultimos_prestamos':        ultimos_prestamos,
        'mis_reservas':             mis_reservas,
        'libros_recientes':         libros_recientes,
    }
    return render(request, 'dashboard/lector.html', context)
