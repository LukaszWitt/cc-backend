import os
import smtplib
from email.message import EmailMessage
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

load_dotenv()

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
TO_EMAIL = os.getenv("TO_EMAIL", SMTP_USER)

app = FastAPI(title="Comfort Connector – Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app$",
    allow_origins=["https://comfortconnector.pl", "https://www.comfortconnector.pl"],  # jeśli używasz własnej domeny
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Contact(BaseModel):
    name: str
    email: EmailStr
    service: str
    message: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/contact")
def contact(data: Contact):
    if not SMTP_USER or not SMTP_PASS:
        return {"ok": False, "error": "Brak konfiguracji SMTP_USER/SMTP_PASS"}

    subject = f"[WWW] Zapytanie – {data.service} – {data.name}"
    body = f"""Imię i nazwisko: {data.name}
Email: {data.email}
Usługa: {data.service}

Wiadomość:
{data.message}
"""

    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)

    return {"ok": True}
