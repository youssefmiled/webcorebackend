from app import db
from app.models.page import Page
from sqlalchemy.exc import IntegrityError


class PageService:

    @staticmethod
    def create_page(website_id: int, data: dict) -> Page:
        """Create a new page for a website."""
        # If this is marked as home, unset any existing home page
        if data.get("is_home"):
            Page.query.filter_by(website_id=website_id, is_home=True).update({"is_home": False})

        page = Page(
            website_id=website_id,
            title=data["title"],
            slug=data["slug"],
            order=data.get("order", 0),
            is_home=data.get("is_home", False),
        )
        db.session.add(page)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"Slug '{data['slug']}' already exists for this website.")
        return page

    @staticmethod
    def get_pages_by_website(website_id: int) -> list[Page]:
        """Return all pages for a website, ordered."""
        return (
            Page.query
            .filter_by(website_id=website_id)
            .order_by(Page.order.asc())
            .all()
        )

    @staticmethod
    def get_page_by_id(page_id: int) -> Page | None:
        """Return a single page by ID."""
        return Page.query.get(page_id)

    @staticmethod
    def update_page(page: Page, data: dict) -> Page:
        """Update page fields. Handles is_home uniqueness."""
        if data.get("is_home") and not page.is_home:
            # Unset any existing home page for this website
            Page.query.filter_by(website_id=page.website_id, is_home=True).update({"is_home": False})

        updatable = ["title", "slug", "order", "is_home"]
        for field in updatable:
            if field in data:
                setattr(page, field, data[field])

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"Slug '{data.get('slug')}' already exists for this website.")
        return page

    @staticmethod
    def delete_page(page: Page) -> None:
        """Delete page and cascade to blocks."""
        db.session.delete(page)
        db.session.commit()
