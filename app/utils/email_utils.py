from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from fastapi import HTTPException
import os
from datetime import datetime, timedelta
import secrets

def generate_verification_token():
    return secrets.token_urlsafe(32)

def create_verification_token():
    token = generate_verification_token()
    expires = datetime.utcnow() + timedelta(days=1)
    return {"token": token, "expires": expires}

def is_token_valid(token_expires):
    if datetime.utcnow() > token_expires:
        return False
    return True

async def send_verification_email(user_email: str, user_name: str, token: str):
    sg = SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
    
    verification_url = f"http://localhost:3000/verify?token={token}"
    
    # Use your template ID from SendGrid
    template_data = {
        "name": user_name,
        "verification_link": verification_url
    }
    
    try:
        message = Mail(
            from_email=Email("junhuohezhang@gmail.com"),
            to_emails=To(user_email),
            subject="Verify your LicitaYa account",
        )
        
        # Add your template ID here
        message.template_id = "d-57f5d6d514ec4539ab6c8e6e08fb4d45"
        message.dynamic_template_data = template_data
        
        response = sg.send(message)
        return response.status_code == 202
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send verification email: {str(e)}"
        )