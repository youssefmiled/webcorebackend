from flask_mail import Message
from extensions import mail

def send_2fa_email(user_email, code):
    msg = Message(subject="Votre code 2FA",
                  sender="noreply@votreapp.com",
                  recipients=[user_email])
    msg.body = f"Votre code de vérification est : {code}"
    mail.send(msg)