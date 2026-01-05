from odoo import models

class ApartmentplugOffer(models.Model):
    _inherit = "apartmentplug.offer"

    def action_accept(self):
        res = super().action_accept()

        for record in self:
            self.env["account.move"].create({
                "move_type": "out_invoice",
                "partner_id": record.partner_id.id,
                "invoice_date": record.date_created,
                "invoice_line_ids": [
                    (0, 0, {
                        "name": f"Property Sale: {record.property_id.display_name}",
                        "quantity": 1.0,
                        "price_unit": record.price,
                    })
                ],
            })

        return res
