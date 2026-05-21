# catalogo/urls.py
from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    # Página de inicio → lista de libros
    path('', views.libro_lista, name='inicio'),

    # Libros
    path('libros/', views.libro_lista, name='libro_lista'),
    path('libros/nuevo/', views.libro_crear, name='libro_crear'),
    path('libros/<int:pk>/', views.libro_detalle, name='libro_detalle'),
    path('libros/<int:pk>/editar/', views.libro_editar, name='libro_editar'),
    path('libros/<int:pk>/eliminar/', views.libro_eliminar, name='libro_eliminar'),

    # Autores
    path('autores/', views.autor_lista, name='autor_lista'),
    path('autores/nuevo/', views.autor_crear, name='autor_crear'),
    path('autores/<int:pk>/', views.autor_detalle, name='autor_detalle'),
    path('autores/<int:pk>/editar/', views.autor_editar, name='autor_editar'),
    path('autores/<int:pk>/eliminar/', views.autor_eliminar, name='autor_eliminar'),

    # Categorías
    path('categorias/', views.categoria_lista, name='categoria_lista'),
    path('categorias/nueva/', views.categoria_crear, name='categoria_crear'),
    path('categorias/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', views.categoria_eliminar, name='categoria_eliminar'),
]