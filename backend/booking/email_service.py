import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_confirmation_email(to_email: str, name: str, date: str, time: str, details: dict = None) -> bool:
    """
    Sends a real confirmation email using SMTP credentials from env.
    Falls back to console log if credentials are missing.
    """
    if not to_email:
        print("DEBUG: Email Service skipped (No email provided)")
        return False
        
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    
    # Construct Email Content
    service_name = details.get('service', 'Service') if details else 'Service'
    subject = f"Confirmation: {service_name} at Aura Aesthetics"
    
    body = f"""
    Dear {name or 'Valued Client'},
    
    We are delighted to confirm your appointment at Aura Aesthetics.
    
    ✨ Service: {service_name}
    📅 Date: {date}
    ⏰ Time: {time}
    
    Location: Aura Aesthetics Studio, Downtown
    
    Please arrive 5 minutes early. If you need to reschedule, simply ask our AI agent.
    
    Warm regards,
    The Aura Aesthetics Team
    """

    # SIMULATION MODE (Default if no creds)
    if not sender_email or not sender_password:
        print(f"\n[EMAIL SIMULATION] ---------------------------------------------")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        print(f"----------------------------------------------------------------\n")
        print("NOTE: Set EMAIL_ADDRESS and EMAIL_PASSWORD in .env to enable real sending.\n")
        return True # Return true so the UI thinks it worked
        
    # REAL SENDING MODE
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to Gmail SMTP (Standard)
        # Note: App Password is required for Gmail if 2FA is on
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        
        print(f"DEBUG: Real email sent to {to_email}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to send email. {e}")
        return False
