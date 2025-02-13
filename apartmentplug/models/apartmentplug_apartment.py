import random
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class ApartmentPlugApartment(models.Model):
    _name = "apartmentplug.apartment"
    _description = "apartmentplug apartment"

    def _get_default_availability_date(self):
        return fields.Date.today() + timedelta(days=30)

    name = fields.Char(
        required=True,
        default="Unknown",
        copy=False,
        index=True,
        help="Name of the apartment",
        string="Apartment Name",
    )
    property_type_id = fields.Many2one(
        comodel_name="apartmentplug.property.type",
        string="Property Type",
        required=True,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Seller",
        required=True,
        copy=False,
        index=True,
        help="Owner of the apartment",
        default=lambda self: self.env.user,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Buyer",
        domain=[("is_company", "=", False)],
        copy=False,
        readonly=True,
        index=True,
    )
    description = fields.Text()
    tags_ids = fields.Many2many(
        comodel_name="apartmentplug.apartment.tag", string="Tags"
    )
    postcode = fields.Char()
    date_availability = fields.Date(
        default=fields.Date.today, copy=False, string="Available From"
    )
    expected_price = fields.Float(default=0.00)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Float(
        default=0.00,
        string="Living Area (sqm)",
    )
    facades = fields.Integer(default=0)
    garage = fields.Boolean(default=False)
    garden = fields.Boolean(default=False)
    garden_area = fields.Float(
        default=0.00,
        string="Garden Area (sqm)",
    )
    garden_orientation = fields.Selection(
        selection=[
            ("north", "North"),
            ("east", "East"),
            ("west", "West"),
            ("south", "South"),
        ],
    )
    state = fields.Selection(
        string="Status",
        required=True,
        selection=[
            ("new", "New"),
            ("offer received", "Offer Received"),
            ("offer accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        compute="_compute_state",
        copy=False,
    )
    total_area = fields.Float(
        string="Total Area (sqm)",
        readonly=True,
        compute="_compute_total_area",
    )
    best_offer = fields.Float(
        readonly=True,
        compute="_compute_best_offer",
    )
    offer_ids = fields.One2many(
        comodel_name="apartmentplug.offer", inverse_name="property_id", string="Offers"
    )
    color = fields.Integer(
        string="Color Index", default=lambda self: self._get_default_color()
    )

    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "check_expected_price",
            "CHECK(expected_price >= 0)",
            "The expected price must be positive",
        ),
        (
            "check_living_area",
            "CHECK(living_area >= 0)",
            "The living area must be positive",
        ),
        (
            "check_garden_area",
            "CHECK(garden_area >= 0)",
            "The garden area must be positive",
        ),
        (
            "check_bedrooms",
            "CHECK(bedrooms >= 0)",
            "The number of bedrooms must be positive",
        ),
        (
            "check_facades",
            "CHECK(facades >= 0)",
            "The number of facades must be positive",
        ),
    ]

    def _get_default_color(self):
        return random.randint(1, 11)

    @api.constrains("selling_price")
    def _check_selling_price(self):
        for record in self:
            if record.selling_price == 0.0:
                continue
            if record.expected_price * 0.9 > record.selling_price:
                raise ValidationError(
                    _("The selling price must be at least 90% of the expected price")
                )

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids")
    def _compute_best_offer(self):
        for record in self:
            if record.offer_ids:
                record.best_offer = max([item.price for item in record.offer_ids])
            else:
                record.best_offer = 0.0

    @api.depends("offer_ids", "partner_id")
    def _compute_state(self):
        for record in self:
            if record.partner_id:
                record.state = "sold"
            elif record.offer_ids:
                record.state = "offer received"
            else:
                record.state = "new"

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10.00
            self.garden_orientation = "south"
        else:
            self.garden_area = 0.00
            self.garden_orientation = ""

    @api.ondelete(at_uninstall=False)
    def _unlink_except_sold(self):
        for record in self:
            if record.state == "sold":
                raise UserError(
                    _("You cannot delete an apartment with an accepted offer")
                )

    def action_create_invoice(self):
        return True
