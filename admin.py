# admin.py
from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

with app.app_context():
    # Supprimer l'ancien admin s'il existe
    old_admin = User.query.filter_by(email="youssefmiled18@gmail.com").first()
    if old_admin:
        db.session.delete(old_admin)
        db.session.commit()
        print("Ancien admin supprimé")

    # Créer le nouvel admin
    admin = User(
        name="Admin",
        email="youssefmiled18@gmail.com",
        role="admin",
        is_two_fa_enabled=True
    )
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()
    print("Admin créé avec succès")