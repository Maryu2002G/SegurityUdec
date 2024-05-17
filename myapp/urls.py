from django.urls import path, include
from . import views
from .views import QRScannerView
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

urlpatterns = [
    path('', views.index,name='login'),
    path('generate/<int:n>/', views.generate_qr_codes_view, name='generate_qr_codes'),
    path('celador/<int:user_id>/', QRScannerView.as_view(), name='celador_view'),
    path('procesar-codigo-qr/', views.procesar_codigo_qr, name='procesar_codigo_qr'),
    path('custom-login/', views.custom_login, name='custom_login'),
    path('accounts/', include('allauth.urls')),
    path('lider_seguridad/', views.lider_seguridad, name='lider_seguridad'),
    path('marcar-alerta/<int:alerta_id>/', views.marcar_alerta_como_visualizado, name='marcar_alerta'),
    path('guardar-alerta/', views.guardar_alerta, name='guardar_alerta'),
    path('mostrar_formulario/<int:user_id>/', views.mostrar_formulario, name='mostrar_formulario'),
    path('obtener-alerta/<int:alerta_id>/', views.obtener_alerta, name='obtener_alerta'),
    path('detalle_alerta/<int:alerta_id>/', views.detalle_alerta, name='detalle_alerta'),
    path('custom-login-url/', views.custom_login, name='custom_login'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

'''
    path('hello/<str:user>',views.hello),
    path('hello2/<int:id>',views.hello2),
    path('projects/', views.projects),
    path('task/<int:id>', views.tasks),
    path('about2/',views.about2),
    path('stream_camera/', views.stream_camera, name='stream_camera'),
     path('proyecthtml/', views.projecthtml),
    '''