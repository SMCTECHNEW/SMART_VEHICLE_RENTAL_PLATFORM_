"""
Notification Service for Email and SMS
Handles sending emails via SMTP and SMS via provider abstraction
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email notification service using SMTP"""
    
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None
    ) -> bool:
        """Send email using SMTP configuration"""
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("SMTP credentials not configured. Email not sent.")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.SMTP_FROM_EMAIL
            msg['To'] = to_email
            
            # Plain text version
            if body_text:
                part1 = MIMEText(body_text, 'plain')
                msg.attach(part1)
            
            # HTML version
            part2 = MIMEText(body_html, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    def send_registration_email(user_email: str, user_name: str) -> bool:
        """Send registration confirmation email"""
        subject = "Welcome to Smart Vehicle Rental Platform!"
        body_html = f"""
        <html>
        <body>
            <h2>Welcome {user_name}!</h2>
            <p>Thank you for registering with Smart Vehicle Rental Platform.</p>
            <p>Your account has been successfully created.</p>
            <p>You can now browse our vehicles and make bookings.</p>
            <br>
            <p>Best regards,<br>Smart Vehicle Rental Team</p>
        </body>
        </html>
        """
        return EmailService.send_email(user_email, subject, body_html)
    
    @staticmethod
    def send_booking_confirmation_email(
        user_email: str,
        user_name: str,
        booking_id: int,
        vehicle_name: str,
        pickup_date: str,
        return_date: str,
        total_amount: float
    ) -> bool:
        """Send booking confirmation email"""
        subject = f"Booking Confirmation - #{booking_id}"
        body_html = f"""
        <html>
        <body>
            <h2>Booking Confirmed!</h2>
            <p>Dear {user_name},</p>
            <p>Your booking has been confirmed successfully.</p>
            <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Booking ID:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">#{booking_id}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Vehicle:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{vehicle_name}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Pickup Date:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{pickup_date}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Return Date:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{return_date}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Total Amount:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">₹{total_amount:.2f}</td></tr>
            </table>
            <br>
            <p>Thank you for choosing Smart Vehicle Rental Platform!</p>
            <p>Best regards,<br>Smart Vehicle Rental Team</p>
        </body>
        </html>
        """
        return EmailService.send_email(user_email, subject, body_html)
    
    @staticmethod
    def send_payment_success_email(
        user_email: str,
        user_name: str,
        booking_id: int,
        amount: float,
        transaction_id: str
    ) -> bool:
        """Send payment success email"""
        subject = f"Payment Successful - Booking #{booking_id}"
        body_html = f"""
        <html>
        <body>
            <h2>Payment Successful!</h2>
            <p>Dear {user_name},</p>
            <p>Your payment has been processed successfully.</p>
            <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Booking ID:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">#{booking_id}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Amount Paid:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">₹{amount:.2f}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Transaction ID:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{transaction_id}</td></tr>
            </table>
            <br>
            <p>Best regards,<br>Smart Vehicle Rental Team</p>
        </body>
        </html>
        """
        return EmailService.send_email(user_email, subject, body_html)
    
    @staticmethod
    def send_password_reset_email(user_email: str, user_name: str, reset_token: str) -> bool:
        """Send password reset email"""
        reset_link = f"{settings.FRONTEND_URL}/reset-password.html?token={reset_token}"
        subject = "Password Reset Request - Smart Vehicle Rental"
        body_html = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Dear {user_name},</p>
            <p>You have requested to reset your password. Click the link below to proceed:</p>
            <p><a href="{reset_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
            <p>Or copy and paste this link into your browser:</p>
            <p>{reset_link}</p>
            <p><strong>This link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRY} minutes.</strong></p>
            <p>If you did not request this, please ignore this email.</p>
            <br>
            <p>Best regards,<br>Smart Vehicle Rental Team</p>
        </body>
        </html>
        """
        return EmailService.send_email(user_email, subject, body_html)
    
    @staticmethod
    def send_booking_cancellation_email(
        user_email: str,
        user_name: str,
        booking_id: int,
        vehicle_name: str,
        refund_amount: float,
        refund_status: str
    ) -> bool:
        """Send booking cancellation email"""
        subject = f"Booking Cancelled - #{booking_id}"
        body_html = f"""
        <html>
        <body>
            <h2>Booking Cancelled</h2>
            <p>Dear {user_name},</p>
            <p>Your booking has been cancelled successfully.</p>
            <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Booking ID:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">#{booking_id}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Vehicle:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{vehicle_name}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Refund Amount:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">₹{refund_amount:.2f}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Refund Status:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{refund_status}</td></tr>
            </table>
            <br>
            <p>Best regards,<br>Smart Vehicle Rental Team</p>
        </body>
        </html>
        """
        return EmailService.send_email(user_email, subject, body_html)
    
    @staticmethod
    def send_refund_email(
        user_email: str,
        user_name: str,
        booking_id: int,
        refund_amount: float,
        refund_transaction_id: str,
        status: str
    ) -> bool:
        """Send refund status email"""
        subject = f"Refund {status.title()} - Booking #{booking_id}"
        body_html = f"""
        <html>
        <body>
            <h2>Refund {status.title()}</h2>
            <p>Dear {user_name},</p>
            <p>Your refund for booking #{booking_id} has been {status}.</p>
            <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Refund Amount:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">₹{refund_amount:.2f}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Transaction ID:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{refund_transaction_id}</td></tr>
            </table>
            <br>
            <p>Best regards,<br>Smart Vehicle Rental Team</p>
        </body>
        </html>
        """
        return EmailService.send_email(user_email, subject, body_html)
    
    @staticmethod
    def send_driver_assignment_email(
        user_email: str,
        user_name: str,
        booking_id: int,
        driver_name: str,
        driver_phone: str,
        driver_license: str
    ) -> bool:
        """Send driver assignment notification"""
        subject = f"Driver Assigned - Booking #{booking_id}"
        body_html = f"""
        <html>
        <body>
            <h2>Driver Assigned to Your Booking</h2>
            <p>Dear {user_name},</p>
            <p>A driver has been assigned to your booking #{booking_id}.</p>
            <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Driver Name:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{driver_name}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Phone:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{driver_phone}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>License Number:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{driver_license}</td></tr>
            </table>
            <br>
            <p>Best regards,<br>Smart Vehicle Rental Team</p>
        </body>
        </html>
        """
        return EmailService.send_email(user_email, subject, body_html)


class SMSService:
    """SMS notification service with provider abstraction"""
    
    @staticmethod
    def send_sms(phone_number: str, message: str) -> bool:
        """Send SMS using configured provider"""
        if not settings.SMS_PROVIDER or not settings.SMS_API_KEY:
            logger.info(f"SMS provider not configured. Message: {message}")
            return False
        
        try:
            if settings.SMS_PROVIDER.lower() == "twilio":
                return SMSService._send_twilio_sms(phone_number, message)
            elif settings.SMS_PROVIDER.lower() == "msg91":
                return SMSService._send_msg91_sms(phone_number, message)
            else:
                logger.warning(f"Unknown SMS provider: {settings.SMS_PROVIDER}")
                return False
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
            return False
    
    @staticmethod
    def _send_twilio_sms(phone_number: str, message: str) -> bool:
        """Send SMS via Twilio"""
        try:
            from twilio.rest import Client
            client = Client(settings.SMS_API_KEY, settings.SMS_SENDER_ID)
            message = client.messages.create(
                body=message,
                from_=settings.SMS_SENDER_ID,
                to=phone_number
            )
            logger.info(f"Twilio SMS sent: {message.sid}")
            return True
        except ImportError:
            logger.warning("Twilio library not installed")
            return False
        except Exception as e:
            logger.error(f"Twilio SMS failed: {str(e)}")
            return False
    
    @staticmethod
    def _send_msg91_sms(phone_number: str, message: str) -> bool:
        """Send SMS via MSG91"""
        import requests
        try:
            url = "https://api.msg91.com/api/sendhttp.php"
            params = {
                "authkey": settings.SMS_API_KEY,
                "mobiles": phone_number,
                "message": message,
                "sender": settings.SMS_SENDER_ID,
                "route": "4",
                "country": "91"
            }
            response = requests.get(url, params=params, timeout=10)
            logger.info(f"MSG91 SMS response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"MSG91 SMS failed: {str(e)}")
            return False
    
    @staticmethod
    def send_booking_confirmation_sms(phone_number: str, booking_id: int, vehicle_name: str) -> bool:
        """Send booking confirmation SMS"""
        message = f"SmartVehicle: Booking #{booking_id} confirmed for {vehicle_name}. Thank you!"
        return SMSService.send_sms(phone_number, message)
    
    @staticmethod
    def send_otp_sms(phone_number: str, otp: str) -> bool:
        """Send OTP SMS"""
        message = f"SmartVehicle: Your OTP is {otp}. Valid for 10 minutes."
        return SMSService.send_sms(phone_number, message)


# Convenience functions
def send_registration_email(user_email: str, user_name: str) -> bool:
    return EmailService.send_registration_email(user_email, user_name)


def send_booking_confirmation_email(user_email: str, user_name: str, booking_id: int, 
                                    vehicle_name: str, pickup_date: str, return_date: str, 
                                    total_amount: float) -> bool:
    return EmailService.send_booking_confirmation_email(
        user_email, user_name, booking_id, vehicle_name, 
        pickup_date, return_date, total_amount
    )


def send_payment_success_email(user_email: str, user_name: str, booking_id: int,
                               amount: float, transaction_id: str) -> bool:
    return EmailService.send_payment_success_email(
        user_email, user_name, booking_id, amount, transaction_id
    )


def send_password_reset_email(user_email: str, user_name: str, reset_token: str) -> bool:
    return EmailService.send_password_reset_email(user_email, user_name, reset_token)


def send_booking_cancellation_email(user_email: str, user_name: str, booking_id: int,
                                    vehicle_name: str, refund_amount: float, 
                                    refund_status: str) -> bool:
    return EmailService.send_booking_cancellation_email(
        user_email, user_name, booking_id, vehicle_name, refund_amount, refund_status
    )


def send_refund_email(user_email: str, user_name: str, booking_id: int,
                      refund_amount: float, refund_transaction_id: str, status: str) -> bool:
    return EmailService.send_refund_email(
        user_email, user_name, booking_id, refund_amount, refund_transaction_id, status
    )


def send_driver_assignment_email(user_email: str, user_name: str, booking_id: int,
                                 driver_name: str, driver_phone: str, 
                                 driver_license: str) -> bool:
    return EmailService.send_driver_assignment_email(
        user_email, user_name, booking_id, driver_name, driver_phone, driver_license
    )


def send_booking_confirmation_sms(phone_number: str, booking_id: int, vehicle_name: str) -> bool:
    return SMSService.send_booking_confirmation_sms(phone_number, booking_id, vehicle_name)
