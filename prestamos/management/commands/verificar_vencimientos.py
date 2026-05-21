"""
Comando: python manage.py verificar_vencimientos

Revisa préstamos próximos a vencer (≤3 días) y retrasados.
Simula el envío de correo por consola (EMAIL_BACKEND de consola).
En producción, cambiar EMAIL_BACKEND a smtp real.
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Verifica préstamos próximos a vencer y retrasados. Envía notificaciones por correo.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=3,
            help='Días de anticipación para notificar (default: 3)',
        )
        parser.add_argument(
            '--solo-consola',
            action='store_true',
            help='Solo muestra en consola, no envía emails',
        )

    def handle(self, *args, **options):
        from prestamos.models import Prestamo

        dias = options['dias']
        solo_consola = options['solo_consola']
        hoy = timezone.now().date()
        limite = hoy + timedelta(days=dias)

        self.stdout.write(self.style.MIGRATE_HEADING(
            f'\n=== Verificación de vencimientos ({hoy}) ===\n'
        ))

        # ── 1. Préstamos por vencer ──────────────────────────────
        por_vencer = Prestamo.objects.filter(
            estado=Prestamo.ESTADO_ACTIVO,
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=limite,
        ).select_related('usuario', 'libro')

        self.stdout.write(f'Préstamos que vencen en los próximos {dias} días: {por_vencer.count()}')

        for p in por_vencer:
            dias_restantes = (p.fecha_vencimiento - hoy).days
            msg = (
                f'  [{dias_restantes}d] {p.libro.titulo[:40]} → {p.usuario.get_full_name()} '
                f'(vence: {p.fecha_vencimiento})'
            )
            self.stdout.write(self.style.WARNING(msg))

            if not solo_consola:
                asunto = f'[Biblioteca] Tu préstamo vence en {dias_restantes} día(s)'
                cuerpo = (
                    f'Hola {p.usuario.first_name},\n\n'
                    f'Te recordamos que el préstamo del libro "{p.libro.titulo}" '
                    f'vence el {p.fecha_vencimiento}.\n\n'
                    f'Por favor, devuélvelo a tiempo para evitar sanciones.\n\n'
                    f'— Biblioteca Digital'
                )
                try:
                    send_mail(
                        asunto,
                        cuerpo,
                        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'biblioteca@demo.com',
                        [p.usuario.email],
                        fail_silently=True,
                    )
                    self.stdout.write(f'    → Email simulado enviado a {p.usuario.email}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    → Error al enviar email: {e}'))

        # ── 2. Préstamos retrasados — marcar y notificar ─────────
        retrasados = Prestamo.objects.filter(
            estado=Prestamo.ESTADO_ACTIVO,
            fecha_vencimiento__lt=hoy,
        ).select_related('usuario', 'libro')

        self.stdout.write(f'\nPréstamos activos con retraso detectado: {retrasados.count()}')

        for p in retrasados:
            dias_retraso = (hoy - p.fecha_vencimiento).days
            p.estado = Prestamo.ESTADO_RETRASADO
            p.dias_retraso = dias_retraso
            p.save(update_fields=['estado', 'dias_retraso'])

            msg = (
                f'  [+{dias_retraso}d] {p.libro.titulo[:40]} → {p.usuario.get_full_name()} '
                f'(venció: {p.fecha_vencimiento})'
            )
            self.stdout.write(self.style.ERROR(msg))

            if not solo_consola:
                asunto = f'[Biblioteca] Préstamo retrasado — {dias_retraso} día(s)'
                cuerpo = (
                    f'Hola {p.usuario.first_name},\n\n'
                    f'Tu préstamo del libro "{p.libro.titulo}" venció hace {dias_retraso} día(s).\n\n'
                    f'Por favor, devuelve el libro lo antes posible.\n'
                    f'Se aplicará una sanción proporcional al tiempo de retraso.\n\n'
                    f'— Biblioteca Digital'
                )
                try:
                    send_mail(
                        asunto,
                        cuerpo,
                        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'biblioteca@demo.com',
                        [p.usuario.email],
                        fail_silently=True,
                    )
                    self.stdout.write(f'    → Email simulado enviado a {p.usuario.email}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    → Error al enviar email: {e}'))

        self.stdout.write(self.style.SUCCESS('\n✓ Verificación completada.\n'))
        if solo_consola:
            self.stdout.write('  (Modo solo-consola: no se enviaron emails reales)\n')
