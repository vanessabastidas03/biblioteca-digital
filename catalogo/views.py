# catalogo/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Libro, Autor, Categoria
from .forms import FormularioLibro, FormularioAutor, FormularioCategoria, FiltroLibroForm


def decorador_bibliotecario(vista):
    """Decorador que requiere que el usuario sea bibliotecario."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.es_bibliotecario:
            messages.error(request, 'Solo los bibliotecarios pueden realizar esta acción.')
            return redirect('catalogo:libro_lista')
        return vista(request, *args, **kwargs)
    return wrapper


# ─────────────── LIBROS ───────────────

@login_required
def libro_lista(request):
    """Lista de libros con búsqueda y filtros."""
    form_filtro = FiltroLibroForm(request.GET)
    libros = Libro.objects.prefetch_related('autores', 'categorias').all()

    if form_filtro.is_valid():
        q = form_filtro.cleaned_data.get('q')
        categoria = form_filtro.cleaned_data.get('categoria')
        estado = form_filtro.cleaned_data.get('estado')
        tipo = form_filtro.cleaned_data.get('tipo')

        if q:
            libros = libros.filter(
                Q(titulo__icontains=q) |
                Q(isbn__icontains=q) |
                Q(autores__nombre__icontains=q) |
                Q(autores__apellido__icontains=q)
            ).distinct()
        if categoria:
            libros = libros.filter(categorias=categoria)
        if estado:
            libros = libros.filter(estado=estado)
        if tipo:
            libros = libros.filter(tipo=tipo)

    return render(request, 'catalogo/libro_lista.html', {
        'libros': libros,
        'form_filtro': form_filtro,
    })


@login_required
def libro_detalle(request, pk):
    """Detalle de un libro."""
    libro = get_object_or_404(Libro, pk=pk)
    return render(request, 'catalogo/libro_detalle.html', {'libro': libro})


@decorador_bibliotecario
def libro_crear(request):
    """Crear un nuevo libro."""
    if request.method == 'POST':
        form = FormularioLibro(request.POST, request.FILES)
        if form.is_valid():
            libro = form.save()
            messages.success(request, f'Libro "{libro.titulo}" creado exitosamente.')
            return redirect('catalogo:libro_detalle', pk=libro.pk)
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = FormularioLibro()
    return render(request, 'catalogo/libro_form.html', {'form': form, 'accion': 'Crear'})


@decorador_bibliotecario
def libro_editar(request, pk):
    """Editar un libro existente."""
    libro = get_object_or_404(Libro, pk=pk)
    if request.method == 'POST':
        form = FormularioLibro(request.POST, request.FILES, instance=libro)
        if form.is_valid():
            form.save()
            messages.success(request, f'Libro "{libro.titulo}" actualizado.')
            return redirect('catalogo:libro_detalle', pk=libro.pk)
    else:
        form = FormularioLibro(instance=libro)
    return render(request, 'catalogo/libro_form.html', {'form': form, 'accion': 'Editar', 'libro': libro})


@decorador_bibliotecario
def libro_eliminar(request, pk):
    """Eliminar un libro."""
    libro = get_object_or_404(Libro, pk=pk)
    if request.method == 'POST':
        titulo = libro.titulo
        libro.delete()
        messages.success(request, f'Libro "{titulo}" eliminado.')
        return redirect('catalogo:libro_lista')
    return render(request, 'catalogo/libro_confirmar_eliminar.html', {'libro': libro})


# ─────────────── AUTORES ───────────────

@login_required
def autor_lista(request):
    autores = Autor.objects.all()
    q = request.GET.get('q', '')
    if q:
        autores = autores.filter(Q(nombre__icontains=q) | Q(apellido__icontains=q))
    return render(request, 'catalogo/autor_lista.html', {'autores': autores, 'q': q})


@login_required
def autor_detalle(request, pk):
    autor = get_object_or_404(Autor, pk=pk)
    return render(request, 'catalogo/autor_detalle.html', {'autor': autor})


@decorador_bibliotecario
def autor_crear(request):
    if request.method == 'POST':
        form = FormularioAutor(request.POST, request.FILES)
        if form.is_valid():
            autor = form.save()
            messages.success(request, f'Autor "{autor}" creado.')
            return redirect('catalogo:autor_lista')
    else:
        form = FormularioAutor()
    return render(request, 'catalogo/autor_form.html', {'form': form, 'accion': 'Crear'})


@decorador_bibliotecario
def autor_editar(request, pk):
    autor = get_object_or_404(Autor, pk=pk)
    if request.method == 'POST':
        form = FormularioAutor(request.POST, request.FILES, instance=autor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Autor "{autor}" actualizado.')
            return redirect('catalogo:autor_lista')
    else:
        form = FormularioAutor(instance=autor)
    return render(request, 'catalogo/autor_form.html', {'form': form, 'accion': 'Editar'})


@decorador_bibliotecario
def autor_eliminar(request, pk):
    autor = get_object_or_404(Autor, pk=pk)
    if request.method == 'POST':
        nombre = str(autor)
        autor.delete()
        messages.success(request, f'Autor "{nombre}" eliminado.')
        return redirect('catalogo:autor_lista')
    return render(request, 'catalogo/autor_confirmar_eliminar.html', {'autor': autor})


# ─────────────── CATEGORÍAS ───────────────

@login_required
def categoria_lista(request):
    categorias = Categoria.objects.all()
    return render(request, 'catalogo/categoria_lista.html', {'categorias': categorias})


@decorador_bibliotecario
def categoria_crear(request):
    if request.method == 'POST':
        form = FormularioCategoria(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f'Categoría "{cat}" creada.')
            return redirect('catalogo:categoria_lista')
    else:
        form = FormularioCategoria()
    return render(request, 'catalogo/categoria_form.html', {'form': form, 'accion': 'Crear'})


@decorador_bibliotecario
def categoria_editar(request, pk):
    cat = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = FormularioCategoria(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoría "{cat}" actualizada.')
            return redirect('catalogo:categoria_lista')
    else:
        form = FormularioCategoria(instance=cat)
    return render(request, 'catalogo/categoria_form.html', {'form': form, 'accion': 'Editar'})


@decorador_bibliotecario
def categoria_eliminar(request, pk):
    cat = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nombre = cat.nombre
        cat.delete()
        messages.success(request, f'Categoría "{nombre}" eliminada.')
        return redirect('catalogo:categoria_lista')
    return render(request, 'catalogo/categoria_confirmar_eliminar.html', {'cat': cat})