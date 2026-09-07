"""Compatibilidad con las funciones del servicio de correo original."""
from django.core.mail import send_mail
from django.utils.html import escape
from .email_utils import send_contract_email as send_html_email


def send_email(to_email, subject, content):
    return send_html_email(to_email, subject, str(escape(content)))


def send_contract_email(subject, message, from_email, recipient_list, fail_silently=False):
    return send_mail(subject, message, from_email, recipient_list, fail_silently=fail_silently)
