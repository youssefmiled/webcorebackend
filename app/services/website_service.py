# app/services/website_service.py

from app.extensions import db
from app.models.website import Website
from app.models.activity_log import ActivityLog
from datetime import datetime, timezone


def _log(user_id: int, action: str, website: Website, details: str | None = None):
    """Insère un ActivityLog (sans commit — le caller commit)."""
    db.session.add(ActivityLog(
        user_id    = user_id,
        action     = action,
        item_name  = website.name,
        website_id = website.id,
        details    = details,
    ))


class WebsiteService:

    @staticmethod
    def create_website(data: dict) -> Website:
        website = Website(
            name          = data.get("name"),
            description   = data.get("description"),
            template      = data.get("template"),
            primary_color = data.get("primary_color"),
            logo          = data.get("logo"),
            user_id       = data.get("user_id"),
            cms_data      = data.get("cms_data", None),
        )
        db.session.add(website)
        db.session.flush()
        _log(data["user_id"], "CREATE", website,
             details=f"Template: {website.template or 'default'}")
        db.session.commit()
        return website

    @staticmethod
    def get_all_websites(user_id: int, page: int = 1, per_page: int = 20):
        return (
            Website.query
            .filter_by(user_id=user_id)
            .order_by(Website.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    @staticmethod
    def get_website_by_id(website_id: int) -> Website | None:
        return Website.query.get(website_id)

    @staticmethod
    def update_website(website_id: int, data: dict, user_id: int) -> Website | None:
        website = Website.query.get(website_id)
        if not website:
            return None

        # ── Détecte les changements AVANT modification ──────────────────────
        changes = []

        if "name" in data and data["name"] != website.name:
            changes.append(f'Name: "{website.name}" → "{data["name"]}"')
            website.name = data["name"]

        if "description" in data and data["description"] != website.description:
            changes.append("Description updated")
            website.description = data["description"]

        if "template" in data and data["template"] != website.template:
            changes.append(f"Template: {website.template} → {data['template']}")
            website.template = data["template"]

        if "primary_color" in data and data["primary_color"] != website.primary_color:
            changes.append(f"Color: {website.primary_color} → {data['primary_color']}")
            website.primary_color = data["primary_color"]

        if "logo" in data and data["logo"] != website.logo:
            changes.append("Logo updated")
            website.logo = data["logo"]

        # cms_data : on persiste sans log détaillé (trop verbeux)
        if "cms_data" in data:
            website.cms_data = data["cms_data"]

        website.updated_at = datetime.now(timezone.utc)

        # Log uniquement si des champs visibles ont changé
        if changes:
            _log(user_id, "UPDATE", website, details=" | ".join(changes))

        db.session.commit()
        return website

    @staticmethod
    def delete_website(website_id: int, user_id: int) -> Website | None:
        website = Website.query.get(website_id)
        if not website:
            return None
        _log(user_id, "DELETE", website, details=f'Deleted "{website.name}"')
        db.session.flush()
        db.session.delete(website)
        db.session.commit()
        return website

    @staticmethod
    def get_recent_activity(user_id: int, limit: int = 10):
        return (
            ActivityLog.query
            .filter_by(user_id=user_id)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
            .all()
        )
