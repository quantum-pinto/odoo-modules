from odoo import _, api, fields, models


class MacAccountTax(models.Model):
    _name = 'mac.account.tax'
    _description = 'Mac Account Tax'

    name = fields.Char(string='Tax Name', required=True)
    rate = fields.Float(string='Tax Rate', required=True)
    description = fields.Text(string='Description')
