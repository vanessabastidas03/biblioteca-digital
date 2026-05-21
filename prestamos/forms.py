# prestamos/forms.py
from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Reserva, Prestamo


class FormularioReserva(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['notas']
        widgets = {
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones opcionales...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # La reserva expira en 3 días por defecto
        self.fecha_expiracion = timezone.now().date() + timedelta(days=3)


class FormularioPrestamo(forms.ModelForm):
    """Formulario para que el bibliotecario registre un préstamo."""
    class Meta:
        model = Prestamo
        fields = ['fecha_vencimiento', 'observaciones']
        widgets = {
            'fecha_vencimiento': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d'
            ),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones opcionales...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Por defecto, el préstamo vence en 14 días
        if not self.instance.pk:
            self.fields['fecha_vencimiento'].initial = (
                timezone.now().date() + timedelta(days=14)
            ).strftime('%Y-%m-%d')

    def clean_fecha_vencimiento(self):
        fecha = self.cleaned_data['fecha_vencimiento']
        if fecha <= timezone.now().date():
            raise forms.ValidationError('La fecha de vencimiento debe ser futura.')
        return fecha


class FiltroPrestamoForm(forms.Form):
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Prestamo.ESTADOS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar usuario o libro...'})
    )