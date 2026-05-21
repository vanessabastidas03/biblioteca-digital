# prestamos/urls.py
from django.urls import path
from . import views

app_name = 'prestamos'

urlpatterns = [
    # Reservas
    path('reservas/', views.lista_reservas, name='reservas'),
    path('reservas/nueva/<int:libro_pk>/', views.crear_reserva, name='crear_reserva'),
    path('reservas/<int:pk>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),

    # Préstamos
    path('', views.lista_prestamos, name='lista'),
    path('nuevo/', views.crear_prestamo, name='crear_prestamo'),
    path('nuevo/reserva/<int:reserva_pk>/', views.crear_prestamo, name='crear_desde_reserva'),
    path('<int:pk>/', views.detalle_prestamo, name='detalle'),
    path('<int:pk>/devolver/', views.devolver_libro, name='devolver'),

    # Sanciones
    path('sanciones/', views.lista_sanciones, name='sanciones'),

    # Reportes
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('reportes/excel/', views.exportar_excel, name='exportar_excel'),
]