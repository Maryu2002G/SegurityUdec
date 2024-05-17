from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.shortcuts import get_object_or_404
from .templates.vist import camera_stream
from .utils import generate_qr_codes, generate_pdf
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
from django.views.generic import TemplateView
import cv2
from django.template.loader import render_to_string
from django.shortcuts import redirect
import json
from .models import Asignacion, Computador, Persona
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.forms.models import model_to_dict
import base64
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from .models import Alerta
from django.utils.decorators import method_decorator
from django.core import serializers
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import logout
'''  elif user.groups.filter(name='seguridad').exists():
                login(request, user)
                user_id = user.id  # Obtén el ID del usuario
                return redirect('lider_seguridad') '''

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:  # Verifica si el usuario tiene permisos de staff (administrador)
                login(request, user)
                return redirect(reverse('admin:index'))
            elif user.groups.filter(name='celador').exists():
                login(request, user)
                user_id = user.id  # Obtén el ID del usuario
                return redirect('celador_view', user_id=user_id)  # Pasar el ID del usuario como parte de la redirección
            elif user.groups.filter(name='seguridad').exists():
                login(request, user)
                user_id = user.id  # Obtén el ID del usuario
                return redirect('lider_seguridad') 
            else:
                error_message = "No tienes permiso para acceder al panel de administración."
                messages.error(request, error_message)
        else:
            error_message = "Credenciales incorrectas."
            messages.error(request, error_message)

    # Si llega aquí, significa que la solicitud es GET o las credenciales son incorrectas
    # Por lo tanto, debemos renderizar la página de inicio de sesión con los mensajes de error
    return render(request, 'index.html')

# Create your views here.
'''
def stream_camera(request):
    return camera_stream(request)

def hello2(request,id):
    result = id +(3*2)
    print(id)
    return HttpResponse("<h1>Hola %s</h1>" % result)

def about2(request):
    title = 'Django Course About 2!!'
    return render(request,'about.html',{
        'title': title
    })
    
def about(request):
    return HttpResponse('About')

def hello(request,user):
    return HttpResponse("<h1>Hola %s</h1>" % user)

def projecthtml(request):
    projects = Project.objects.all()
    return render(request, 'projects.html',{
        'proyecto':projects
    })

def projects(request):
    project = Project.objects.values()
    p = list(project)
    return JsonResponse(p, safe = False)

def tasks(request,id):
    tas = Task.objects.get(id = id)
    tass = get_object_or_404(Task, id=id)
    return HttpResponse('task:  %s' % tass.tittle)

'''
def index(request):
    return render(request, 'index.html')



class QRScannerView(TemplateView):
    template_name = "celador.html"

    @method_decorator(login_required(login_url='/custom-login/'))  
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id  # Obtén el ID del usuario actual
        context['user_id'] = user_id  # Agrega el ID del usuario al contexto
        return context
    
    def get_frame(self):
        camera = cv2.VideoCapture(0)  
        while True:
            success, frame = camera.read()  
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)  
                frame = buffer.tobytes()  
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
  

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()  # Obtén el contexto
        camera_html = render(request, 'celador.html', {'video_feed': self.get_frame(), 'user_id': context['user_id']})
        return HttpResponse(camera_html)


@login_required
def generate_qr_codes_view(request, n):
    user = request.user
    qr_codes = generate_qr_codes(n, user)
    pdf = generate_pdf(qr_codes)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="qrs.pdf"'
    return response

@csrf_exempt
def procesar_codigo_qr(request):
    if request.method == 'POST':
        # Obtener la información del código QR del cuerpo de la solicitud POST
        data = json.loads(request.body)
        respuesta_qr = data.get('respuesta')
        
        print('Datos recibidos:', respuesta_qr)

        # Realizar la consulta en la base de datos y obtener los datos
        qr_data = consulta_base_de_datos(respuesta_qr)
        if qr_data:
            # Obtener datos del objeto Asignacion
            asignacion_data = model_to_dict(qr_data)
            
            # Obtener datos del objeto Computador relacionado
            computador_data = model_to_dict(qr_data.computador)
            
            ape = qr_data.computador.persona.apellidos
            id_computador = str(computador_data['id'])
            # Obtener nombre de la persona asociada al computador
            nombre_pers= qr_data.computador.persona.name_p
            nombreCompleto = nombre_pers + ' ' + ape
            # Si se encontró el código QR, devolver sus datos en formato JSON
            qr_data_json = {
                'nombre_persona': nombreCompleto,
                'nombre':qr_data.computador.persona.name_p,
                'marca_computador': computador_data['marca'],
                'id': id_computador,
                'id_qr': qr_data.qrcode.code,
                'Identificacion': qr_data.computador.persona.id,
                'rol': qr_data.computador.persona.rol_u,
            }
            #
            print(qr_data_json)
            return JsonResponse(qr_data_json)
        else:
            # Si no se encontró el código QR, devolver un mensaje de error
            mensaje_error = {'error': 'El código QR no fue encontrado en la base de datos'}
            return JsonResponse(mensaje_error, status=404)

def consulta_base_de_datos(respuesta_qr):
    try:
        # Consultar el código QR por el campo 'code'
        asignacion = Asignacion.objects.get(qrcode__code=respuesta_qr)
        return asignacion
    except Asignacion.DoesNotExist:
        # Manejar el caso en que el código QR no exista en la base de datos
        return None

def lider_seguridad(request):
    alertas_pendientes = Alerta.objects.filter(visualisado=False)
    alerta_seleccionada = None
    
    if request.method == 'POST':
        alerta_id = request.POST.get('alerta_id')
        if alerta_id:
            alerta = Alerta.objects.get(id=alerta_id)
            alerta.visualisado = True
            alerta.save()
            alerta_seleccionada = alerta
            return redirect('detalle_alerta', alerta_id=alerta_id)  # Redirige a la página de detalle de la alerta
    
    return render(request, 'lider_seguridad.html', {'alertas_pendientes': alertas_pendientes, 'alerta_seleccionada': alerta_seleccionada})

def detalle_alerta(request, alerta_id):
    alerta = get_object_or_404(Alerta, pk=alerta_id)
    return render(request, 'detalle_alerta.html', {'alerta': alerta})

def marcar_alerta_como_visualizado(request, alerta_id):
    alerta = Alerta.objects.get(id=alerta_id)
    alerta.visualisado = True
    alerta.save()
    return redirect('lider_seguridad')


def guardar_alerta(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')  # Obtener el ID del usuario del formulario
        mensaje = request.POST.get('mensaje')  # Obtener el mensaje del formulario

        # Verificar que el usuario exista
        try:
            usuario = User.objects.get(id=user_id)
        except User.DoesNotExist:
            # Manejar el error si el usuario no existe
            return redirect('error_page')  # Redirigir a una página de error, por ejemplo

        # Crear la alerta
        alerta = Alerta.objects.create(celador=usuario, mensaje=mensaje)

        # Redirigir a alguna página de éxito, por ejemplo, la lista de alertas
        return redirect('celador_view', user_id=user_id)
    
def mostrar_formulario(request, user_id):
    return render(request, 'Formulario_anomalia.html', {'user_id': user_id})

# Asumiendo que 'obtener_anomalia' es tu vista
def obtener_anomalia(request):
    if request.method == 'GET' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        # Lógica para manejar solicitudes AJAX
        id_alerta = request.GET.get('id')
        # Ejemplo: Suponiendo que quieres obtener los detalles de la alerta
        try:
            alerta = Alerta.objects.get(id=id_alerta)
            # Suponiendo que tienes un método en tu modelo Alerta llamado `to_dict` que convierte la alerta a un diccionario
            alerta_data = alerta.to_dict()
            return JsonResponse({'alerta': alerta_data})
        except Alerta.DoesNotExist:
            return JsonResponse({'error': 'Alerta no encontrada'}, status=404)
    else:
        # Lógica para manejar solicitudes que no son AJAX
        # Por ejemplo, si es un GET normal, puedes devolver una página HTML renderizada
        return render(request, 'Lider_Seguridad.html')
    
def obtener_alerta(request, alerta_id):
    try:
        alerta = Alerta.objects.get(id=alerta_id)
        # Serializar la alerta en formato JSON
        alerta_json = serializers.serialize('json', [alerta])
        return JsonResponse({'alerta': alerta_json})
    except Alerta.DoesNotExist:
        return JsonResponse({'error': 'Alerta no encontrada'}, status=404)
    
def custom_logout(request):
    logout(request)
    return redirect('index.html')