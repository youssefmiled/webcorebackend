# backend/app/routes/contact.py

from flask import Blueprint, request, jsonify, current_app
from flask_mail import Message
from app.extensions import db, mail
from app.models.contact import Contact
import re

contact_bp = Blueprint("contact", __name__)

# -------------------------
# Validation email simple
# -------------------------
def is_valid_email(email):
    """Validation simple d'email avec regex."""
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

# -------------------------
# Route pour envoyer message
# -------------------------
@contact_bp.route("/send-message", methods=["POST"])
def send_message():
    """
    Reçoit les données du formulaire (JSON ou formulaire HTML),
    sauvegarde en base et envoie un email.
    """
    # Récupération des données (supporte JSON et formulaire)
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    # Validation des champs requis
    if not name or not email or not message:
        return jsonify({"error": "Tous les champs sont requis"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Adresse email invalide"}), 400

    # 1️⃣ Sauvegarde en base de données
    new_contact = Contact(name=name, email=email, message=message)
    db.session.add(new_contact)
    db.session.commit()

    # 2️⃣ Envoi de l'email avec rendu HTML amélioré
    try:
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background: #f4f6fb; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px;">
                <h2 style="color:#2563eb;">Nouveau message de contact</h2>
                <p><strong>Nom :</strong> {name}</p>
                <p><strong>Email :</strong> {email}</p>
                <hr>
                <p><strong>Message :</strong></p>
                <p>{message}</p>
                <hr>
                <p style="font-size: 12px; color: #888;">© 2026 WebCore Platform</p>
            </div>
        </body>
        </html>
        """

        msg = Message(
            subject=f"Message de {name} via le formulaire de contact",
            recipients=["youssefmiled18@gmail.com"],  # Destinataire fixe
            reply_to=email,
            html=html_content
        )
        mail.send(msg)
    except Exception as e:
        # En production, logger l'erreur
        current_app.logger.error(f"Erreur envoi email : {e}")
        return jsonify({
            "error": "Le message a été sauvegardé mais l'email n'a pas pu être envoyé."
        }), 500

    return jsonify({"message": "Message envoyé avec succès"}), 201