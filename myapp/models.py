from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Persona(models.Model):
    id = models.IntegerField(primary_key=True)
    name_p = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    
    TIPO_DOCUMENTO_CHOICES = (
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería'),
    )
    TIPO_USER = (
        ('Adm', 'Administrador'),
        ('Estud', 'Estudiante'),
        ('Ext', 'Externo'),
    )
    TIPO_CARRERA = (
        ('IS', 'Ingeniería de Sistemas'),
        ('IA', 'Ingeniería Ambiental'),
        ('IAG', 'Ingeniería Agronómica'),
        ('AD', 'Administración de Empresas'),
        ('CP', 'Contaduría Pública'),
    )

    tip_doc = models.CharField(max_length=2, choices=TIPO_DOCUMENTO_CHOICES)
    numeric_validator = RegexValidator(regex=r'^[0-9]*$', message='Este campo solo puede contener números.')
    correo = models.CharField(max_length=100)
    phone_num = models.CharField(max_length=10, validators=[numeric_validator])
    rol_u = models.CharField(max_length=50, choices=TIPO_USER)
    carrera = models.CharField(max_length=50, choices=TIPO_CARRERA, null=True, blank=True)

    def clean(self):
        # Validación personalizada para requerir 'carrera' si 'rol_u' es 'Estud'
        if self.rol_u == 'Estud' and not self.carrera:
            raise ValidationError({'carrera': 'La carrera es obligatoria para los estudiantes.'})

    def __str__(self):
        return f"{self.name_p} {self.apellidos}"

class Computador(models.Model):
    id = models.AutoField(primary_key=True)
    marca = models.CharField(max_length=20)
    modelo = models.CharField(max_length=40)
    imagen = models.BinaryField(null=True, blank=True)
    color = models.CharField(max_length=7)
    descripcion = models.CharField(max_length=100)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    assigned = models.BooleanField(default=False)
    def __str__(self):
        return self.marca
    
class QRCode(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=255, unique=True)
    encrypted_data = models.TextField()
    create_for = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    assigned_at = models.DateTimeField(default=timezone.now)
    is_assigned = models.BooleanField(default=False)
    computador = models.ForeignKey('Computador', on_delete=models.SET_NULL, null=True, blank=True)  

    def save(self, *args, **kwargs):
        if self.is_assigned and not self.computador:
            raise ValueError("Si is_assigned es True, el campo computador debe ser especificado")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code
class Asignacion(models.Model):
    computador = models.ForeignKey(Computador, on_delete=models.CASCADE)
    qrcode = models.ForeignKey(QRCode, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('computador', 'qrcode')  # Para asegurar que cada asignación sea única
        

class CrearQR(models.Model):
    total = models.IntegerField(primary_key=True)
    fecha = models.DateTimeField(default=timezone.now)
    
class Alerta(models.Model):
    mensaje = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    visualisado = models.BooleanField(default=False)
    celador = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    #vinculadoa = models.ForeignKey(Persona, on_delete=models.CASCADE)
    #generado_por = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return self.mensaje
    def to_dict(self):
        return {
            'id': self.id,
            'mensaje': self.mensaje,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'), # Formatea la fecha si es necesario
        }
