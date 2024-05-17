from django.http import HttpResponseRedirect
from django.urls import reverse

class SuperuserRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si el usuario intenta acceder al panel de administración
        if request.path.startswith(reverse('admin:index')):
            # Si el usuario no está autenticado o no es superusuario
            if not request.user.is_authenticated or not request.user.is_superuser:
                # Redirigir al usuario a tu vista de inicio de sesión personalizada
                custom_login_url = reverse('custom_login')
                return HttpResponseRedirect(custom_login_url)
        # Si el usuario está autenticado y es superusuario, o si no está accediendo al panel de administración, continuar normalmente
        return self.get_response(request)
