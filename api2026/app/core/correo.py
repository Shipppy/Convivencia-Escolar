"""Envio de correo: Brevo por HTTPS (si hay BREVO_API_KEY) o SMTP."""
import base64
import json
import os
import smtplib
import urllib.error
import urllib.request
from email.message import EmailMessage

from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()


def enviar_correo(destino, asunto, cuerpo, nombre_archivo, contenido, mime):
    api_key = os.getenv("BREVO_API_KEY")
    if api_key:
        remitente = os.getenv("EMAIL_FROM")
        if not remitente:
            raise HTTPException(503, "Falta EMAIL_FROM (remitente verificado en Brevo)")
        payload = {
            "sender": {"name": os.getenv("EMAIL_FROM_NAME", "Convivencia Escolar"), "email": remitente},
            "to": [{"email": destino}],
            "subject": asunto,
            "textContent": cuerpo,
            "attachment": [{"name": nombre_archivo, "content": base64.b64encode(contenido).decode()}],
        }
        req = urllib.request.Request(
            "https://api.brevo.com/v3/smtp/email",
            data=json.dumps(payload).encode(),
            headers={"api-key": api_key, "content-type": "application/json", "accept": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=30)
        except urllib.error.URLError as e:
            print(f"Error Brevo: {e}")
            raise HTTPException(502, "No fue posible enviar el correo")
        return

    host = os.getenv("SMTP_HOST")
    usuario = os.getenv("SMTP_USER")
    if not host or not usuario:
        raise HTTPException(503, "El envío por correo no está configurado")
    msg = EmailMessage()
    msg["Subject"], msg["To"] = asunto, destino
    msg["From"] = os.getenv("SMTP_FROM") or usuario
    msg.set_content(cuerpo)
    tipo, _, subtipo = mime.partition("/")
    msg.add_attachment(contenido, maintype=tipo, subtype=subtipo, filename=nombre_archivo)
    try:
        with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587")), timeout=30) as s:
            s.starttls()
            s.login(usuario, os.getenv("SMTP_PASSWORD", ""))
            s.send_message(msg)
    except Exception as e:
        print(f"Error SMTP: {e}")
        raise HTTPException(502, "No fue posible enviar el correo")
