from django import forms
from django.contrib.auth.forms import UserCreationForm
import dns.resolver
from django.contrib.auth.models import User, Group

class CustomUserCreationForm(UserCreationForm):
    ROLES = [
        ('administrador', 'Administrador'),
        ('celador', 'Celador'),
        ('seguridad', 'Seguridad')
    ]

    email = forms.EmailField(label='Email')
    roles = forms.ChoiceField(choices=ROLES, label='Rol')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Verificar que el correo electrónico tenga el dominio correcto
        if not email.endswith('@ucundinamarca.edu.co'):
            raise forms.ValidationError('El correo electrónico debe ser del dominio @ucundinamarca.edu.co')

        return email
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'roles', 'password1', 'password2')