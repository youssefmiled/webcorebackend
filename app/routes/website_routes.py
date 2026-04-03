# app/routes/website_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload

from app.services.website_service import WebsiteService
from app.schemas.website_schema import website_schema, websites_schema
from app.models.page import Page

website_bp = Blueprint("websites", __name__, url_prefix="/api/websites")


# ─── Helper local ─────────────────────────────────────────────────────────────

def _get_owned_website(website_id: int):
    user_id = int(get_jwt_identity())
    website = WebsiteService.get_website_by_id(website_id)
    if not website:
        return None, (jsonify({"message": "Website not found"}), 404)
    if website.user_id != user_id:
        return None, (jsonify({"message": "Unauthorized"}), 403)
    return website, None


# ─── CRUD standard ────────────────────────────────────────────────────────────

@website_bp.route("", methods=["POST"])
@jwt_required()
def create_website():
    user_id = int(get_jwt_identity())
    data = request.json or {}
    if not data.get("name"):
        return jsonify({"message": "Name is required"}), 400
    data["user_id"] = user_id
    website = WebsiteService.create_website(data)
    return jsonify({"message": "Website created successfully", "website": website_schema.dump(website)}), 201


@website_bp.route("", methods=["GET"])
@jwt_required()
def get_websites():
    user_id = int(get_jwt_identity())
    page   = request.args.get("page", 1, type=int)
    result = WebsiteService.get_all_websites(user_id=user_id, page=page)
    return jsonify({
        "websites":     websites_schema.dump(result.items),
        "total":        result.total,
        "pages":        result.pages,
        "current_page": result.page,
    })


@website_bp.route("/<int:website_id>", methods=["GET"])
@jwt_required()
def get_website(website_id):
    website, err = _get_owned_website(website_id)
    if err:
        return err
    return jsonify(website_schema.dump(website))


@website_bp.route("/<int:website_id>", methods=["PUT"])
@jwt_required()
def update_website(website_id):
    website, err = _get_owned_website(website_id)
    if err:
        return err
    data    = request.json or {}
    updated = WebsiteService.update_website(website_id, data, user_id=int(get_jwt_identity()))
    return jsonify({"message": "Website updated successfully", "website": website_schema.dump(updated)})


@website_bp.route("/<int:website_id>", methods=["DELETE"])
@jwt_required()
def delete_website(website_id):
    website, err = _get_owned_website(website_id)
    if err:
        return err
    WebsiteService.delete_website(website_id, user_id=int(get_jwt_identity()))
    return jsonify({"message": "Website deleted successfully"})


# ─── Activity ──────────────────────────────────────────────────────────────────

@website_bp.route("/activity", methods=["GET"])
@jwt_required()
def get_activity():
    user_id = int(get_jwt_identity())
    limit   = request.args.get("limit", 10, type=int)
    logs    = WebsiteService.get_recent_activity(user_id=user_id, limit=limit)
    return jsonify({"activity": [log.to_dict() for log in logs]})


# ─── CMS : sauvegarde (bouton Save + autosave du CMSEditor) ───────────────────

@website_bp.route("/<int:website_id>/cms", methods=["PUT"])
@jwt_required()
def save_cms(website_id):
    """
    Appelé par CMSEditor pour sauvegarder pages + globalStyles.

    Body attendu :
    {
        "pages":        [...],
        "globalStyles": { ... }
    }
    """
    website, err = _get_owned_website(website_id)
    if err:
        return err

    body = request.json or {}

    # Accepte { cms_data: {...} } ou { pages: [...], globalStyles: {...} }
    if "cms_data" in body:
        cms_data = body["cms_data"]
    else:
        cms_data = {
            "pages":        body.get("pages", []),
            "globalStyles": body.get("globalStyles", {}),
        }

    updated = WebsiteService.update_website(
        website_id,
        {"cms_data": cms_data},
        user_id=int(get_jwt_identity()),
    )

    return jsonify({
        "message":  "CMS saved",
        "cms_data": updated.cms_data,
    }), 200


# ─── CMS : structure complète (tables pages + blocks) ─────────────────────────

@website_bp.route("/<int:website_id>/full", methods=["GET"])
@jwt_required()
def get_full_website(website_id):
    """
    Retourne website (avec cms_data) + pages/blocks depuis les tables dédiées.
    """
    website, err = _get_owned_website(website_id)
    if err:
        return err

    pages = (
        Page.query
        .filter_by(website_id=website_id)
        .options(joinedload(Page.blocks))
        .order_by(Page.order.asc())
        .all()
    )

    pages_data = [
        {
            "id":      page.id,
            "title":   page.title,
            "slug":    page.slug,
            "order":   page.order,
            "is_home": page.is_home,
            "blocks": [
                {"id": b.id, "type": b.type, "order": b.order, "props": b.props or {}}
                for b in sorted(page.blocks, key=lambda b: b.order)
            ],
        }
        for page in pages
    ]

    return jsonify({
        "website": website_schema.dump(website),
        "pages":   pages_data,
    }), 200
