from django.contrib import admin
from .models import Persona, Computador, QRCode, Asignacion, CrearQR
from django.utils.html import format_html
from django.urls import reverse
from django import forms
from django.utils.safestring import mark_safe
import base64
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User, Group
from .forms import CustomUserCreationForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'roles', 'password1', 'password2'),
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.save()
        
        # Asignar al grupo correspondiente
        role = form.cleaned_data.get('roles')
        if role:
            group = Group.objects.get(name=role)
            obj.groups.add(group)

        super().save_model(request, obj, form, change)
            
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class PersonaAdminForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        rol_u = cleaned_data.get('rol_u')
        carrera = cleaned_data.get('carrera')
        
        if rol_u == 'Estud' and not carrera:
            self.add_error('carrera', 'La carrera es obligatoria para los estudiantes.')

        return cleaned_data

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    form = PersonaAdminForm
    list_display = ('name_p', 'apellidos', 'tip_doc', 'correo', 'phone_num', 'rol_u', 'carrera')
    search_fields = ('name_p', 'apellidos', 'correo')


class ComputadorAdminForm(forms.ModelForm):
    imagen = forms.FileField(label='Imagen', required=False)
    class Meta:
        
        model = Computador
        exclude = ['imagen'] 

@admin.register(Computador)
class ComputadorAdmin(admin.ModelAdmin):
    list_display = ['id', 'marca', 'modelo', 'imagen_display', 'color', 'descripcion', 'persona', 'assigned']
    readonly_fields = ['assigned']
    form = ComputadorAdminForm  # Asignar el formulario personalizado

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('imagen'):  # Verifica si se proporcionó una imagen en el formulario
            imagen = form.cleaned_data['imagen']
            obj.imagen = imagen.read()  # Lee los datos binarios de la imagen y los asigna al campo 'imagen'
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ['assigned']
    
    def imagen_display(self, obj):
        if obj.imagen:
            # Codifica los datos binarios de la imagen en formato base64
            imagen_base64 = base64.b64encode(obj.imagen).decode('utf-8')  # Decodifica los datos binarios a una cadena utf-8
            return format_html('<img src="data:image/png;base64,{}" style="max-height:200px; max-width:200px;" />'.format(imagen_base64))
        else:
            return "No hay imagen"

    imagen_display.short_description = 'Imagen' 
    
@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'create_for', 'assigned_at', 'is_assigned', 'computador', 'computador_brand']
    readonly_fields = ['id', 'code', 'create_for', 'assigned_at', 'is_assigned', 'computador']
    def has_add_permission(self, request):
        return False
    
    def computador_id(self, obj):
        return obj.computador.id if obj.computador else None
    
    computador_id.short_description = 'ID del Computador'

    def computador_brand(self, obj):
        return obj.computador.marca if obj.computador else 'null'
    
    computador_brand.short_description = 'Marca del Computador'


class AsignacionForm(forms.ModelForm):
    class Meta:
        model = Asignacion
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        computador = cleaned_data.get('computador')
        qrcode = cleaned_data.get('qrcode')

        if qrcode and qrcode.is_assigned:
            raise forms.ValidationError("El QRCode ya está asignado a un Computador.")
        
        return cleaned_data


class AsignacionAdmin(admin.ModelAdmin):
    form = AsignacionForm
    list_display = ('computador', 'qrcode', 'fecha_asignacion')
    list_filter = ('fecha_asignacion',)
    search_fields = ('computador__marca', 'qrcode__code')

    def save_model(self, request, obj, form, change):
        # Realizar validaciones
        if obj.qrcode.is_assigned:
            raise ValueError("El QRCode ya está asignado a un Computador.")
        
        # Llamar al método save_model de la clase base para guardar la asignación
        super().save_model(request, obj, form, change)
        
        # Actualizar el QRCode para marcarlo como asignado
        obj.qrcode.is_assigned = True
        obj.qrcode.computador = obj.computador
        obj.qrcode.save()

        # Actualizar el Computador para marcarlo como asignado
        obj.computador.assigned = True
        obj.computador.save()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "qrcode":
            kwargs["queryset"] = QRCode.objects.filter(is_assigned=False)
        if db_field.name == "computador":
            kwargs["queryset"] = Computador.objects.filter(assigned=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Asignacion, AsignacionAdmin)
    
from django.http import HttpResponseRedirect
from django.db.models import Sum




class QrCodeAdmin(admin.ModelAdmin):
    # Define la acción personalizada para el botón
    def enviar_a_url(self, request, queryset):
        # Obtener el total de la tabla qrg
        total = CrearQR.objects.aggregate(total=Sum('total'))['total']
        if total is None:
            total = 0
        # Obtener la URL de la vista de generación de códigos QR con el total como parámetro
        url = reverse('generate_qr_codes', args=[total])
        # Redirigir a la URL
        return HttpResponseRedirect(url)
    
    enviar_a_url.short_description = "Crear QRs"

    # Lista de campos a mostrar en el admin
    list_display = ('total', 'fecha')
    actions = ['enviar_a_url']

admin.site.register(CrearQR, QrCodeAdmin)