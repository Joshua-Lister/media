"""
Email service for sending notifications.

**IMPORTANT: UPDATE EMAIL CONFIGURATION**
Before using this service, update your .env file with:
- EMAIL_HOST=smtp.gmail.com (or your SMTP server)
- EMAIL_PORT=587
- EMAIL_USERNAME=your-email@gmail.com
- EMAIL_PASSWORD=your-app-password
- EMAIL_FROM=noreply@yourdomain.com
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from jinja2 import Template

from app.core.config import settings


class EmailService:
    """Service for sending emails."""

    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email.

        **REQUIRES: Email configuration in .env file**

        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML email content
            text_content: Optional plain text content

        Returns:
            bool: True if sent successfully
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = settings.EMAIL_FROM
            message["To"] = to_email
            message["Subject"] = subject

            # Add text part if provided
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)

            # Add HTML part
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_USERNAME,
                password=settings.EMAIL_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS,
            )

            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    @staticmethod
    async def send_verification_email(email: str, username: str, token: str) -> bool:
        """
        Send email verification email.

        Args:
            email: User email
            username: Username
            token: Verification token

        Returns:
            bool: True if sent successfully
        """
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #0ea5e9; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background-color: #f9f9f9; }
                .button { display: inline-block; padding: 12px 24px; background-color: #0ea5e9;
                         color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Citizen Journalism!</h1>
                </div>
                <div class="content">
                    <h2>Hello {{ username }}!</h2>
                    <p>Thank you for signing up. Please verify your email address to get started.</p>
                    <p>
                        <a href="{{ verification_url }}" class="button">Verify Email</a>
                    </p>
                    <p>Or copy this link: <br>{{ verification_url }}</p>
                    <p>This link will expire in 24 hours.</p>
                </div>
                <div class="footer">
                    <p>If you didn't create an account, please ignore this email.</p>
                    <p>&copy; 2024 Citizen Journalism Platform</p>
                </div>
            </div>
        </body>
        </html>
        """

        template = Template(html_template)
        html_content = template.render(username=username, verification_url=verification_url)

        return await EmailService.send_email(
            to_email=email,
            subject="Verify your email - Citizen Journalism",
            html_content=html_content,
        )

    @staticmethod
    async def send_password_reset_email(email: str, username: str, token: str) -> bool:
        """Send password reset email."""
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #0ea5e9; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background-color: #f9f9f9; }
                .button { display: inline-block; padding: 12px 24px; background-color: #0ea5e9;
                         color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Hello {{ username }}!</h2>
                    <p>We received a request to reset your password.</p>
                    <p>
                        <a href="{{ reset_url }}" class="button">Reset Password</a>
                    </p>
                    <p>Or copy this link: <br>{{ reset_url }}</p>
                    <p>This link will expire in 1 hour.</p>
                </div>
                <div class="footer">
                    <p>If you didn't request this, please ignore this email.</p>
                    <p>&copy; 2024 Citizen Journalism Platform</p>
                </div>
            </div>
        </body>
        </html>
        """

        template = Template(html_template)
        html_content = template.render(username=username, reset_url=reset_url)

        return await EmailService.send_email(
            to_email=email,
            subject="Reset your password - Citizen Journalism",
            html_content=html_content,
        )

    @staticmethod
    async def send_article_published_notification(
        email: str, username: str, article_title: str, article_url: str
    ) -> bool:
        """Send notification when article is published."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #0ea5e9; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background-color: #f9f9f9; }
                .button { display: inline-block; padding: 12px 24px; background-color: #0ea5e9;
                         color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Your Article is Live!</h1>
                </div>
                <div class="content">
                    <h2>Congratulations {{ username }}!</h2>
                    <p>Your article "<strong>{{ article_title }}</strong>" has been published.</p>
                    <p>
                        <a href="{{ article_url }}" class="button">View Article</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        template = Template(html_template)
        html_content = template.render(
            username=username, article_title=article_title, article_url=article_url
        )

        return await EmailService.send_email(
            to_email=email,
            subject=f"Your article '{article_title}' is now live!",
            html_content=html_content,
        )

    @staticmethod
    async def send_new_follower_notification(
        email: str, username: str, follower_name: str
    ) -> bool:
        """Send notification when someone follows you."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .content { padding: 20px; background-color: #f9f9f9; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <h2>Hello {{ username }}!</h2>
                    <p><strong>{{ follower_name }}</strong> started following you!</p>
                    <p>Keep creating great content to engage your audience.</p>
                </div>
            </div>
        </body>
        </html>
        """

        template = Template(html_template)
        html_content = template.render(username=username, follower_name=follower_name)

        return await EmailService.send_email(
            to_email=email,
            subject=f"{follower_name} started following you",
            html_content=html_content,
        )
