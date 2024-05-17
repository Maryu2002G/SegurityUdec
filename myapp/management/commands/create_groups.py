from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Creates necessary groups for the application'

    def handle(self, *args, **options):
        # Crear los grupos si no existen
        Group.objects.get_or_create(name='administrador')
        Group.objects.get_or_create(name='celador')
        Group.objects.get_or_create(name='Seguridad')

        self.stdout.write(self.style.SUCCESS('Grupos creados exitosamente'))