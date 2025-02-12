from odoo import fields, models


class LetterSignTemplate(models.Model):
    _inherit = "sign.template"

    letter_ids = fields.One2many(
        comodel_name="letter.letter", inverse_name="sign_template_id", string="Letters"
    )
