from django.contrib import admin
from .models import Categoria, Autor, Libro


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'color']
    search_fields = ['nombre']


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ['apellido', 'nombre', 'nacionalidad']
    search_fields = ['nombre', 'apellido']


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'isbn', 'estado', 'tipo', 'ejemplares_disponibles']
    list_filter = ['estado', 'tipo', 'categorias']
    search_fields = ['titulo', 'isbn']
    filter_horizontal = ['autores', 'categorias']