from marshmallow import Schema, fields

class WebsiteSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    template = fields.Str()
    primary_color = fields.Str()
    logo = fields.Str()
    created_at = fields.DateTime()
    user_id = fields.Int()

website_schema = WebsiteSchema()
websites_schema = WebsiteSchema(many=True)