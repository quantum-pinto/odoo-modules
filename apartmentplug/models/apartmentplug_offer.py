from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ApartmentplugOffer(models.Model):
    _name = "apartmentplug.offer"
    _description = "apartmentplug.offer"

    price = fields.Float(copy=False)
    status = fields.Selection(
        selection=[
            ("new", "New"),
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        readonly=True,
        default="new",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Customer", required=True
    )
    property_id = fields.Many2one(
        comodel_name="apartmentplug.apartment", string="Apartment", required=True
    )
    is_enough = fields.Boolean(compute="_compute_is_enough")

    property_type_id = fields.Many2one(
        comodel_name="apartmentplug.property.type",
        string="Property Type",
        related="property_id.property_type_id",
        store=True,
    )
    date_created = fields.Date(default=fields.Date.today, readonly=True)

    _sql_constraints_ = [
        ("check_price", "CHECK(price >= 0)", "The price must be positive")
    ]

    @api.depends("price", "property_id")
    def _compute_is_enough(self):
        for record in self:
            record.is_enough = record.price >= record.property_id.expected_price * 0.9

    def action_accept(self):
        accepted_offer = self.env["apartmentplug.offer"].search(
            [
                ("property_id", "=", self.property_id.id),
                ("status", "=", "accepted"),
                ("id", "!=", self.id),
            ]
        )

        if accepted_offer:
            raise ValidationError(
                _("Another offer has already been accepted for this property")
            )

        other_offers = self.env["apartmentplug.offer"].search(
            [
                ("property_id", "=", self.property_id.id),
                ("status", "=", "new"),
                ("id", "!=", self.id),
            ]
        )

        for offer in other_offers:
            offer.status = "refused"

        self.status = "accepted"

        self.property_id.state = "offer accepted"
        self.property_id.selling_price = self.price
        self.property_id.partner_id = self.partner_id

        return True

    def action_refuse(self):
        if self.status == "accepted":
            self.property_id.state = "offer received"
            self.property_id.selling_price = 0.0
            self.property_id.partner_id = False
        self.status = "refused"
        return True
