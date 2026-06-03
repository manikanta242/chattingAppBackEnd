from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from core.config import FRONTEND_URL

from core.config import (
    MAIL_USERNAME, MAIL_PASSWORD,
    MAIL_FROM, MAIL_PORT, MAIL_SERVER
)

conf = ConnectionConfig(
    MAIL_USERNAME   = MAIL_USERNAME,
    MAIL_PASSWORD   = MAIL_PASSWORD,
    MAIL_FROM       = MAIL_FROM,
    MAIL_PORT       = MAIL_PORT,
    MAIL_SERVER     = MAIL_SERVER,
    MAIL_STARTTLS   = True,
    MAIL_SSL_TLS    = False,
    USE_CREDENTIALS = True
)

async def sendVerificationEmail(email: str, token: str):
    verify_url = f"{FRONTEND_URL}/verify-email?token={token}"

    message = MessageSchema(
        subject    = "Verify Your Email - Chat App",
        recipients = [email],
        body       = f"""
            <div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto;">
                <h2>Welcome to Chat App! 👋</h2>
                <p>Click the button below to verify your email and activate your account.</p>
                <a href="{verify_url}"
                   style="display:inline-block; padding:12px 24px;
                          background:#0084ff; color:white;
                          border-radius:8px; text-decoration:none;
                          font-size:16px; margin:16px 0;">
                   ✅ Verify Email
                </a>
                <p style="color:#888; font-size:12px;">
                    This link expires in 24 hours.
                    If you didn't register, ignore this email.
                </p>
            </div>
        """,
        subtype = "html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    
async def sendResetPasswordEmail(email: str, token: str):
    reset_url = f"{FRONTEND_URL}/reset-password?token={token}"

    message = MessageSchema(
        subject    = "Reset Your Password - Chat App",
        recipients = [email],
        body       = f"""
            <div style="font-family:Arial,sans-serif; max-width:500px; margin:auto;">
                <h2>Reset Your Password 🔐</h2>
                <p>We received a request to reset your password.</p>
                <a href="{reset_url}"
                   style="display:inline-block; padding:12px 24px;
                          background:#0084ff; color:white;
                          border-radius:8px; text-decoration:none;
                          font-size:16px; margin:16px 0;">
                   Reset Password
                </a>
                <p style="color:#888; font-size:12px;">
                    This link expires in 1 hour.
                    If you didn't request this, ignore this email.
                </p>
            </div>
        """,
        subtype = "html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    
    
async def resendEmalLink(email, token):
    verification_url = f"{FRONTEND_URL}/verify-email?token={token}"
    
    message = MessageSchema(
        subject="Verify your ChatApp email",
        recipients=[email],
        body=f"Click to verify your email: {verification_url}",
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)