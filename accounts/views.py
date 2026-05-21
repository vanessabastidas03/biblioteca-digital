# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from .forms import FormularioRegistro, FormularioLogin, FormularioPerfil
from .models import Usuario


def registro(request):
    """Vista para que nuevos usuarios se registren."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = FormularioRegistro(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f'¡Bienvenido/a {usuario.first_name}! Tu cuenta fue creada exitosamente.')
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = FormularioRegistro()

    return render(request, 'accounts/registro.html', {'form': form})


def iniciar_sesion(request):
    """Vista de inicio de sesión."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = FormularioLogin(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            messages.success(request, f'¡Bienvenido/a de nuevo, {usuario.first_name}!')
            # next_url viene del query param; si no existe, redirige al dashboard
            next_url = request.GET.get('next') or '/dashboard/'
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = FormularioLogin()

    return render(request, 'accounts/login.html', {'form': form})


def cerrar_sesion(request):
    """Vista para cerrar sesión."""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('accounts:login')


@login_required
def perfil(request):
    """Vista del perfil del usuario — se adapta según el rol (lector o bibliotecario)."""
    if request.method == 'POST':
        form = FormularioPerfil(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('accounts:perfil')
    else:
        form = FormularioPerfil(instance=request.user)

    context = {'form': form}

    if request.user.es_bibliotecario:
        # Estadísticas para el bibliotecario — imports diferidos para evitar
        # ciclos de importación y fallos si las apps no están listas
        try:
            from catalogo.models import Libro
            from prestamos.models import Prestamo, Reserva, Sancion
            context.update({
                'total_libros':          Libro.objects.count(),
                'libros_disponibles':    Libro.objects.filter(estado='disponible').count(),
                'libros_prestados':      Libro.objects.filter(estado='prestado').count(),
                'libros_reservados':     Libro.objects.filter(estado='reservado').count(),
                'prestamos_activos':     Prestamo.objects.filter(estado='activo').count(),
                'prestamos_retrasados':  Prestamo.objects.filter(estado='retrasado').count(),
                'prestamos_devueltos':   Prestamo.objects.filter(estado='devuelto').count(),
                'reservas_pendientes':   Reserva.objects.filter(estado='pendiente').count(),
                'sanciones_activas':     Sancion.objects.filter(activa=True).count(),
                'total_lectores':        Usuario.objects.filter(rol=Usuario.ROL_LECTOR).count(),
                'total_usuarios':        Usuario.objects.count(),
            })
        except Exception:
            pass  # Si algo falla, el template muestra 0 sin romper
    else:
        # Estadísticas personales del lector
        try:
            from prestamos.models import Prestamo, Reserva
            hoy = timezone.now().date()
            mis_prestamos = Prestamo.objects.filter(usuario=request.user)
            context.update({
                'mis_prestamos_activos':   mis_prestamos.filter(estado='activo').count(),
                'mis_prestamos_retrasados':mis_prestamos.filter(estado='retrasado').count(),
                'mis_prestamos_total':     mis_prestamos.count(),
                'mis_reservas_activas':    Reserva.objects.filter(
                                               usuario=request.user,
                                               estado='pendiente',
                                           ).count(),
                'sancionado':              request.user.sancionado,
                'fecha_fin_sancion':       request.user.fecha_fin_sancion,
            })
        except Exception:
            pass

    return render(request, 'accounts/perfil.html', context)


@login_required
def lista_usuarios(request):
    """Lista de usuarios — solo para bibliotecarios."""
    if not request.user.es_bibliotecario:
        messages.error(request, 'No tienes permiso para acceder a esta sección.')
        return redirect('dashboard:index')

    usuarios = Usuario.objects.all().order_by('-date_joined')
    return render(request, 'accounts/lista_usuarios.html', {'usuarios': usuarios})