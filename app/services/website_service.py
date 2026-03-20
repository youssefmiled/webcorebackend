from app.extensions import db
from app.models.website import Website


class WebsiteService:

    @staticmethod
    def create_website(data):
        website = Website(
            name=data.get("name"),
            description=data.get("description"),
            template=data.get("template"),
            primary_color=data.get("primary_color"),
            logo=data.get("logo"),
            user_id=data.get("user_id")
        )

        db.session.add(website)
        db.session.commit()

        return website


    @staticmethod
    def get_all_websites():
        return Website.query.all()


    @staticmethod
    def get_website_by_id(website_id):
        return Website.query.get(website_id)


    @staticmethod
    def update_website(website_id, data):

        website = Website.query.get(website_id)

        if not website:
            return None

        website.name = data.get("name", website.name)
        website.description = data.get("description", website.description)
        website.template = data.get("template", website.template)
        website.primary_color = data.get("primary_color", website.primary_color)
        website.logo = data.get("logo", website.logo)

        db.session.commit()

        return website


    @staticmethod
    def delete_website(website_id):

        website = Website.query.get(website_id)

        if not website:
            return None

        db.session.delete(website)
        db.session.commit()

        return website