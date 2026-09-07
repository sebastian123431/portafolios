import base64
import os

from django.conf import settings
from django.template.loader import render_to_string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Attachment,
    Disposition,
    FileContent,
    FileName,
    FileType,
    Mail,
)

from .models import trabajadores
from .services.availability import EmailUnavailable


def send_contract_email(to_email, subject, html_content, attachment_path=None):
    """
    Envía un correo electrónico utilizando SendGrid con una opción para adjuntar un contrato.

    :param to_email: Dirección de correo del destinatario.
    :param subject: Asunto del correo.
    :param html_content: Contenido HTML del correo.
    :param attachment_path: Ruta del archivo a adjuntar.
    :return: Respuesta de la API o error.
    """
    # Configuración del remitente
    from_email = settings.DEFAULT_FROM_EMAIL
    sendgrid_api_key = settings.SENDGRID_API_KEY

    if not sendgrid_api_key:
        raise EmailUnavailable("La clave API de SendGrid no está configurada.")

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )

    if attachment_path:
        with open(attachment_path, "rb") as f:
            file_data = f.read()
            encoded_file = base64.b64encode(file_data).decode()
            attached_file = Attachment(
                FileContent(encoded_file),
                FileName(os.path.basename(attachment_path)),
                FileType("application/pdf"),
                Disposition("attachment"),
            )
            message.attachment = attached_file

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        if not 200 <= response.status_code < 300:
            raise EmailUnavailable("SendGrid no aceptó el correo.")
        return response
    except Exception as e:
        raise EmailUnavailable("No se pudo enviar el correo mediante SendGrid. Revisa la configuración del servicio.") from e


def enviar_correos_personalizados():
    trabajadores_lista = trabajadores.objects.all()
    for trabajador in trabajadores_lista:
        subject = f"Hola {trabajador.nombre}, este es tu correo personalizado"
        html_content = render_to_string(
            "contratos_agiles/plantilla_correo.html", {"nombre": trabajador.nombre}
        )
        send_contract_email(
            to_email=trabajador.correo, subject=subject, html_content=html_content
        )
