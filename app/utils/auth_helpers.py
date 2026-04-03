from flask import jsonify
from flask_jwt_extended import get_jwt_identity

# Import your Website model — adjust path to match your project
from app.models.website import Website
from app.models.page import Page
from app.models.block import Block


def get_current_user_id() -> int:
    return int(get_jwt_identity())


def get_owned_website(website_id: int):
    """
    Returns website if it belongs to the current JWT user.
    Returns (None, error_response) if not found or unauthorized.
    """
    user_id = get_current_user_id()
    website = Website.query.get(website_id)
    if not website:
        return None, (jsonify({"error": "Website not found"}), 404)
    if website.user_id != user_id:
        return None, (jsonify({"error": "Forbidden"}), 403)
    return website, None


def get_owned_page(page_id: int):
    """
    Returns (page, None) if page belongs to one of the current user's websites.
    Returns (None, error_response) otherwise.
    """
    user_id = get_current_user_id()
    page = Page.query.get(page_id)
    if not page:
        return None, (jsonify({"error": "Page not found"}), 404)
    website = Website.query.get(page.website_id)
    if not website or website.user_id != user_id:
        return None, (jsonify({"error": "Forbidden"}), 403)
    return page, None


def get_owned_block(block_id: int):
    """
    Returns (block, None) if block belongs to a page of the current user's website.
    Returns (None, error_response) otherwise.
    """
    user_id = get_current_user_id()
    block = Block.query.get(block_id)
    if not block:
        return None, (jsonify({"error": "Block not found"}), 404)
    page = Page.query.get(block.page_id)
    if not page:
        return None, (jsonify({"error": "Block not found"}), 404)
    website = Website.query.get(page.website_id)
    if not website or website.user_id != user_id:
        return None, (jsonify({"error": "Forbidden"}), 403)
    return block, None
