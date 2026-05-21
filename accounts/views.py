# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
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
    """Vista del perfil del usuario."""
    if request.method == 'POST':
        form = FormularioPerfil(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('accounts:perfil')
    else:
        form = FormularioPerfil(instance=request.user)

    return render(request, 'accounts/perfil.html', {'form': form})


@login_required
def lista_usuarios(request):
    """Lista de usuarios — solo para bibliotecarios."""
    if not request.user.es_bibliotecario:
        messages.error(request, 'No tienes permiso para acceder a esta sección.')
        return redirect('dashboard:index')

    usuarios = Usuario.objects.all().order_by('-date_joined')
    return render(request, 'accounts/lista_usuarios.html', {'usuarios': usuarios})