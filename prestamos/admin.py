from django.contrib import admin
from .models import Reserva, Prestamo, Sancion


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'libro', 'fecha_reserva', 'estado']
    list_filter = ['estado']
    search_fields = ['usuario__username', 'libro__titulo']


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'libro', 'fecha_prestamo', 'fecha_vencimiento', 'estado']
    list_filter = ['estado']
    search_fields = ['usuario__username', 'libro__titulo']


@admin.register(Sancion)
class SancionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'dias_sancion', 'fecha_inicio', 'fecha_fin', 'activa']
    list_filter = ['activa']