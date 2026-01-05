from odoo import models, fields, _
from odoo.exceptions import UserError

class ApartmentPlugOfferAccount(models.Model):
    _inherit = 'apartmentplug.offer'

    def action_refuse(self):
        return super().action_refuse()

    def action_accept(self):
        # 1️⃣ Call the original logic first
        res = super().action_accept()

        # 2️⃣ Create invoice ONLY after successful acceptance
        for offer in self:
            offer._create_customer_invoice()

        return res


    def _create_customer_invoice(self):
        self.ensure_one()

        if not self.partner_id:
            raise UserError(_("Cannot create invoice without a customer."))

        # Find a sales journal
        journal = self.env['account.journal'].search(
            [('type', '=', 'sale')], limit=1
        )
        if not journal:
            raise UserError(_("No Sales Journal found."))

        # Create the invoice
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'journal_id': journal.id,
            'invoice_origin': self.property_id.name,
            'invoice_line_ids': [(0, 0, {
                'name': f'Apartment Offer - {self.property_id.name}',
                'quantity': 1,
                'price_unit': self.price,
            })],
        })

        return invoice

