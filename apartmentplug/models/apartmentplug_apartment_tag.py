from odoo import fields, models


class ApartmentPlugApartmentTag(models.Model):
    _name = "apartmentplug.apartment.tag"
    _description = "apartmentplug apartment tag"

    name = fields.Char(required=True, copy=False, string="Tag Name")
    description = fields.Text()
    color = fields.Integer(string="Color Index")
    active = fields.Boolean(default=True)

    _sql_constraints = [("name_uniq", "unique (name)", "Tag name must be unique")]
