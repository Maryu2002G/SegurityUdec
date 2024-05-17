import base64
import qrcode
from PIL import Image
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import secrets
from cryptography.fernet import Fernet
from django.utils import timezone
from .models import QRCode
import math
import os

key = Fernet.generate_key()
cipher_suite = Fernet(key)

def generate_qr_codes(n, user):
    qr_codes = []
    for _ in range(n):
        code = generate_random_code()
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(code)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        data = f"QR Code generado por: {user.username}"
        encrypted_data = encrypt_data(data)

        qr_obj = QRCode.objects.create(
            code=code,
            encrypted_data=encrypted_data,
            create_for=user,
            is_assigned=False,
            assigned_at=timezone.now()
        )

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        qr_codes.append((img_str, code))

    return qr_codes

def generate_pdf(qr_codes):
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)

    qr_codes_per_page = 4
    total_pages = math.ceil(len(qr_codes) / qr_codes_per_page)
    
    for page_num in range(1, total_pages+1):
        pdf.showPage()
        pdf.setFont("Helvetica", 12)
        y = 600

        for i in range(qr_codes_per_page):
            index = (page_num - 1) * qr_codes_per_page +i
            if index >= len(qr_codes):
                break

            qr_code, code = qr_codes[index]
            img_data = base64.b64decode(qr_code)
            img = Image.open(BytesIO(img_data))

            img_path = f"qr_{code}.png"
            img.save(img_path)
            pdf.drawImage(img_path, x=100, y=y, width=200, height=200)
            pdf.drawString(350, y + 100, f"Código: {code}")
            y -= 200
            
            os.remove(img_path)

    pdf.save()
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


def generate_random_code(length=10):
    return secrets.token_hex(length)

def encrypt_data(data):
    data_bytes = data.encode('utf-8')
    encrypted_data = cipher_suite.encrypt(data_bytes)
    return encrypted_data