from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ApartmentPlugPropertyType(models.Model):
    _name = "apartmentplug.property.type"
    _description = "apartmentplug property type"

    name = fields.Char(required=True, copy=False, string="Apartment Type")
    description = fields.Text()
    apartment_ids = fields.One2many(
        "apartment.line", "apartment_id", string="Apartments"
    )
    active = fields.Boolean(default=True)
    offer_ids = fields.One2many(
        comodel_name="apartmentplug.offer",
        inverse_name="property_type_id",
        string="Offers",
    )
    offer_count = fields.Integer(compute="_compute_offer_count")

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    _sql_constraints = [("name_uniq", "unique (name)", "Property Type must be unique")]

    @api.ondelete(at_uninstall=False)
    def _unlink_except_contain_apartment(self):
        for record in self:
            if record.apartment_ids:
                raise UserError(
                    _("You cannot delete a property type that contains apartments")
                )


class ApartmentLine(models.Model):
    _name = "apartment.line"
    _description = "apartment line"

    apartment_id = fields.Many2one(
        comodel_name="apartmentplug.property.type",
        readonly=True,
    )
    name = fields.Char()
    user_id = fields.Many2one(
        comodel_name="res.partner", string="Seller", required=True
    )
    bedrooms = fields.Integer()
    expected_price = fields.Float()
