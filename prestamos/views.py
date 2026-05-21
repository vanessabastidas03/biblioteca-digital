# prestamos/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta, date
from catalogo.models import Libro
from .models import Reserva, Prestamo, Sancion
from .forms import FormularioReserva, FormularioPrestamo, FiltroPrestamoForm


# ─────────────── RESERVAS ───────────────

@login_required
def lista_reservas(request):
    """Lista de reservas. El bibliotecario ve todas; el lector solo las suyas."""
    if request.user.es_bibliotecario:
        reservas = Reserva.objects.select_related('usuario', 'libro').all()
    else:
        reservas = Reserva.objects.filter(usuario=request.user)

    return render(request, 'prestamos/lista_reservas.html', {'reservas': reservas})


@login_required
def crear_reserva(request, libro_pk):
    """Crear una reserva para un libro."""
    libro = get_object_or_404(Libro, pk=libro_pk)

    # Verificar que el usuario no esté sancionado
    if request.user.sancionado:
        messages.error(request, 'No puedes reservar libros mientras estés sancionado.')
        return redirect('catalogo:libro_detalle', pk=libro_pk)

    # Verificar disponibilidad
    if not libro.esta_disponible:
        messages.error(request, 'Este libro no está disponible para reserva.')
        return redirect('catalogo:libro_detalle', pk=libro_pk)

    # Verificar que no tenga una reserva activa del mismo libro
    reserva_existente = Reserva.objects.filter(
        usuario=request.user,
        libro=libro,
        estado__in=['pendiente', 'confirmada']
    ).exists()
    if reserva_existente:
        messages.warning(request, 'Ya tienes una reserva activa para este libro.')
        return redirect('catalogo:libro_detalle', pk=libro_pk)

    if request.method == 'POST':
        form = FormularioReserva(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            reserva.libro = libro
            reserva.fecha_expiracion = timezone.now().date() + timedelta(days=3)
            reserva.save()

            # Actualizar estado del libro si es el único ejemplar
            if libro.ejemplares_disponibles == 1:
                libro.estado = Libro.ESTADO_RESERVADO
            libro.ejemplares_disponibles -= 1
            libro.save()

            messages.success(
                request,
                f'Reserva del libro "{libro.titulo}" creada. '
                f'Tienes hasta el {reserva.fecha_expiracion} para recogerlo.'
            )
            return redirect('prestamos:reservas')
    else:
        form = FormularioReserva()

    return render(request, 'prestamos/crear_reserva.html', {'form': form, 'libro': libro})


@login_required
def cancelar_reserva(request, pk):
    """Cancelar una reserva."""
    reserva = get_object_or_404(Reserva, pk=pk)

    # Solo el propio usuario o el bibliotecario pueden cancelar
    if request.user != reserva.usuario and not request.user.es_bibliotecario:
        messages.error(request, 'No tienes permiso para cancelar esta reserva.')
        return redirect('prestamos:reservas')

    if request.method == 'POST':
        reserva.estado = Reserva.ESTADO_CANCELADA
        reserva.save()

        # Devolver el ejemplar
        libro = reserva.libro
        libro.ejemplares_disponibles += 1
        if libro.ejemplares_disponibles > 0:
            libro.estado = Libro.ESTADO_DISPONIBLE
        libro.save()

        messages.success(request, 'Reserva cancelada correctamente.')
        return redirect('prestamos:reservas')

    return render(request, 'prestamos/cancelar_reserva.html', {'reserva': reserva})


# ─────────────── PRÉSTAMOS ───────────────

@login_required
def lista_prestamos(request):
    """Lista de préstamos con filtros."""
    form_filtro = FiltroPrestamoForm(request.GET)

    if request.user.es_bibliotecario:
        prestamos = Prestamo.objects.select_related('usuario', 'libro').all()
    else:
        prestamos = Prestamo.objects.filter(usuario=request.user)

    if form_filtro.is_valid():
        estado = form_filtro.cleaned_data.get('estado')
        fecha_desde = form_filtro.cleaned_data.get('fecha_desde')
        fecha_hasta = form_filtro.cleaned_data.get('fecha_hasta')
        q = form_filtro.cleaned_data.get('q')

        if estado:
            prestamos = prestamos.filter(estado=estado)
        if fecha_desde:
            prestamos = prestamos.filter(fecha_prestamo__date__gte=fecha_desde)
        if fecha_hasta:
            prestamos = prestamos.filter(fecha_prestamo__date__lte=fecha_hasta)
        if q:
            prestamos = prestamos.filter(
                Q(usuario__username__icontains=q) |
                Q(usuario__first_name__icontains=q) |
                Q(libro__titulo__icontains=q)
            )

    # Actualizar estados retrasados automáticamente
    hoy = timezone.now().date()
    prestamos_activos_retrasados = prestamos.filter(
        estado=Prestamo.ESTADO_ACTIVO,
        fecha_vencimiento__lt=hoy
    )
    prestamos_activos_retrasados.update(estado=Prestamo.ESTADO_RETRASADO)

    return render(request, 'prestamos/lista_prestamos.html', {
        'prestamos': prestamos,
        'form_filtro': form_filtro,
    })


@login_required
def crear_prestamo(request, reserva_pk=None):
    """Crear un préstamo (solo bibliotecarios). Puede venir de una reserva."""
    if not request.user.es_bibliotecario:
        messages.error(request, 'Solo el bibliotecario puede registrar préstamos.')
        return redirect('prestamos:lista')

    reserva = None
    libro = None

    if reserva_pk:
        reserva = get_object_or_404(Reserva, pk=reserva_pk)
        libro = reserva.libro
        usuario = reserva.usuario
    else:
        libro_pk = request.GET.get('libro')
        if libro_pk:
            libro = get_object_or_404(Libro, pk=libro_pk)

    if request.method == 'POST':
        form = FormularioPrestamo(request.POST)
        if form.is_valid():
            prestamo = form.save(commit=False)
            prestamo.libro = libro
            prestamo.usuario = usuario if reserva else request.user  # En producción: seleccionar usuario
            prestamo.reserva = reserva
            prestamo.save()

            # Actualizar reserva
            if reserva:
                reserva.estado = Reserva.ESTADO_CONFIRMADA
                reserva.save()

            # Actualizar libro
            libro.estado = Libro.ESTADO_PRESTADO
            libro.save()

            messages.success(
                request,
                f'Préstamo registrado. Vence el {prestamo.fecha_vencimiento}.'
            )
            return redirect('prestamos:lista')
    else:
        form = FormularioPrestamo()

    return render(request, 'prestamos/crear_prestamo.html', {
        'form': form,
        'reserva': reserva,
        'libro': libro,
    })


@login_required
def devolver_libro(request, pk):
    """Registrar la devolución de un libro."""
    if not request.user.es_bibliotecario:
        messages.error(request, 'Solo el bibliotecario puede registrar devoluciones.')
        return redirect('prestamos:lista')

    prestamo = get_object_or_404(Prestamo, pk=pk)

    if request.method == 'POST':
        prestamo.fecha_devolucion = timezone.now()

        hoy = timezone.now().date()
        if hoy > prestamo.fecha_vencimiento:
            dias_retraso = (hoy - prestamo.fecha_vencimiento).days
            prestamo.dias_retraso = dias_retraso
            prestamo.estado = Prestamo.ESTADO_RETRASADO

            # Crear sanción (1 día de sanción por cada día de retraso)
            dias_sancion = dias_retraso * 2  # 2 días de sanción por día de retraso
            fecha_fin_sancion = hoy + timedelta(days=dias_sancion)

            Sancion.objects.create(
                usuario=prestamo.usuario,
                prestamo=prestamo,
                fecha_fin=fecha_fin_sancion,
                dias_sancion=dias_sancion,
                motivo=f'Retraso de {dias_retraso} día(s) en la devolución de "{prestamo.libro.titulo}"'
            )

            # Sancionar al usuario
            prestamo.usuario.sancionado = True
            prestamo.usuario.fecha_fin_sancion = fecha_fin_sancion
            prestamo.usuario.save()

            messages.warning(
                request,
                f'Libro devuelto con {dias_retraso} días de retraso. '
                f'Se aplicó sanción hasta el {fecha_fin_sancion}.'
            )
        else:
            prestamo.estado = Prestamo.ESTADO_DEVUELTO
            messages.success(request, 'Libro devuelto exitosamente a tiempo.')

        prestamo.save()

        # Actualizar libro
        libro = prestamo.libro
        libro.ejemplares_disponibles += 1
        if libro.ejemplares_disponibles > 0:
            libro.estado = Libro.ESTADO_DISPONIBLE
        libro.save()

        return redirect('prestamos:lista')

    return render(request, 'prestamos/devolver_libro.html', {'prestamo': prestamo})


@login_required
def detalle_prestamo(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    if request.user != prestamo.usuario and not request.user.es_bibliotecario:
        messages.error(request, 'No tienes permiso para ver este préstamo.')
        return redirect('prestamos:lista')
    return render(request, 'prestamos/detalle_prestamo.html', {'prestamo': prestamo})


@login_required
def lista_sanciones(request):
    """Lista de sanciones activas."""
    if request.user.es_bibliotecario:
        sanciones = Sancion.objects.select_related('usuario', 'prestamo').all()
    else:
        sanciones = Sancion.objects.filter(usuario=request.user)
    return render(request, 'prestamos/lista_sanciones.html', {'sanciones': sanciones})