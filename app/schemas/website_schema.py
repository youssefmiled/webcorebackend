# app/schemas/website_schema.py

from marshmallow import Schema, fields


class WebsiteSchema(Schema):
    id            = fields.Int(dump_only=True)
    name          = fields.Str(required=True)
    description   = fields.Str()
    template      = fields.Str()
    primary_color = fields.Str()
    logo          = fields.Str()
    user_id       = fields.Int()
    created_at    = fields.DateTime()
    updated_at    = fields.DateTime()

    # ← NOUVEAU : retourne cms_data tel quel (dict ou None)
    cms_data      = fields.Raw(allow_none=True)


website_schema  = WebsiteSchema()
websites_schema = WebsiteSchema(many=True)
