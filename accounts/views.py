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
            if usuario.es_bibliotecario:
                return redirect('dashboard:index')
            return redirect('dashboard:lector')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = FormularioRegistro()

    return render(request, 'accounts/registro.html', {'form': form})


def iniciar_sesion(request):
    """Vista de inicio de sesión con validación de rol."""
    if request.user.is_authenticated:
        if request.user.es_bibliotecario:
            return redirect('dashboard:index')
        return redirect('dashboard:lector')

    if request.method == 'POST':
        form = FormularioLogin(request, data=request.POST)
        rol_solicitado = request.POST.get('rol_solicitado', 'lector')

        if form.is_valid():
            usuario = form.get_user()

            # Validación de rol
            if rol_solicitado == 'bibliotecario' and not usuario.es_bibliotecario:
                messages.error(request, 'Tu cuenta no tiene permisos de bibliotecario.')
                return render(request, 'accounts/login.html', {
                    'form': form,
                    'rol_solicitado': rol_solicitado,
                })

            login(request, usuario)
            messages.success(request, f'¡Bienvenido/a de nuevo, {usuario.first_name}!')

            # Respetar parámetro ?next= si existe (ej: @login_required redirect)
            next_url = request.GET.get('next', '').strip()
            if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                return redirect(next_url)

            # Redirigir según rol real del usuario
            if usuario.es_bibliotecario:
                return redirect('dashboard:index')
            return redirect('dashboard:lector')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = FormularioLogin()
        rol_solicitado = 'lector'

    return render(request, 'accounts/login.html', {
        'form': form,
        'rol_solicitado': rol_solicitado,
    })


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
        return redirect('dashboard:lector')

    usuarios = Usuario.objects.all().order_by('-date_joined')
    return render(request, 'accounts/lista_usuarios.html', {'usuarios': usuarios})


@login_required
def usuario_detalle(request, pk):
    """Detalle de un usuario — solo para bibliotecarios."""
    if not request.user.es_bibliotecario:
        messages.error(request, 'No tienes permiso para acceder a esta sección.')
        return redirect('dashboard:lector')

    usuario = get_object_or_404(Usuario, pk=pk)

    # Estadísticas del usuario
    stats = {}
    try:
        from prestamos.models import Prestamo, Reserva, Sancion
        mis_prestamos = Prestamo.objects.filter(usuario=usuario)
        stats = {
            'prestamos_total':     mis_prestamos.count(),
            'prestamos_activos':   mis_prestamos.filter(estado='activo').count(),
            'prestamos_retrasados':mis_prestamos.filter(estado='retrasado').count(),
            'prestamos_devueltos': mis_prestamos.filter(estado='devuelto').count(),
            'reservas_pendientes': Reserva.objects.filter(usuario=usuario, estado='pendiente').count(),
            'sanciones_total':     Sancion.objects.filter(usuario=usuario).count(),
        }
    except Exception:
        pass

    context = {
        'usuario_detalle': usuario,
        'stats': stats,
    }
    return render(request, 'accounts/usuario_detalle.html', context)


@login_required
def usuario_editar(request, pk):
    """Editar datos básicos de un usuario — solo para bibliotecarios."""
    if not request.user.es_bibliotecario:
        messages.error(request, 'No tienes permiso para acceder a esta sección.')
        return redirect('dashboard:lector')

    usuario = get_object_or_404(Usuario, pk=pk)
    es_mi_cuenta = (usuario.pk == request.user.pk)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()

        usuario.first_name = first_name
        usuario.last_name  = last_name
        usuario.email      = email

        # No permitir que el admin cambie su propio rol ni se desactive a sí mismo
        if not es_mi_cuenta:
            nuevo_rol = request.POST.get('rol', usuario.rol)
            if nuevo_rol in [Usuario.ROL_LECTOR, Usuario.ROL_BIBLIOTECARIO]:
                usuario.rol = nuevo_rol
            is_active = request.POST.get('is_active') == '1'
            usuario.is_active = is_active

        usuario.save()
        messages.success(request, f'Usuario {usuario.username} actualizado correctamente.')
        return redirect('accounts:usuario_detalle', pk=usuario.pk)

    context = {
        'usuario_editar': usuario,
        'es_mi_cuenta': es_mi_cuenta,
        'roles': Usuario.ROLES,
    }
    return render(request, 'accounts/usuario_form.html', context)
