# catalogo/forms.py
from django import forms
from .models import Libro, Autor, Categoria


class FormularioCategoria(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'color']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }


class FormularioAutor(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ['nombre', 'apellido', 'biografia', 'nacionalidad', 'foto']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'biografia': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }


class FormularioLibro(forms.ModelForm):
    class Meta:
        model = Libro
        fields = [
            'titulo', 'isbn', 'autores', 'categorias', 'editorial',
            'anio_publicacion', 'descripcion', 'portada', 'tipo',
            'cantidad_ejemplares', 'ejemplares_disponibles', 'ubicacion'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'autores': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '4'}),
            'categorias': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '4'}),
            'editorial': forms.TextInput(attrs={'class': 'form-control'}),
            'anio_publicacion': forms.NumberInput(attrs={'class': 'form-control', 'min': 1000, 'max': 2030}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'portada': forms.FileInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_ejemplares': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'ejemplares_disponibles': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'autores': 'Autores (mantén Ctrl para seleccionar varios)',
            'categorias': 'Categorías (mantén Ctrl para seleccionar varias)',
        }


class FiltroLibroForm(forms.Form):
    """Formulario de búsqueda y filtros para libros."""
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por título, autor o ISBN...'
        })
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        empty_label='Todas las categorías',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Libro.ESTADOS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tipo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + Libro.TIPOS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )