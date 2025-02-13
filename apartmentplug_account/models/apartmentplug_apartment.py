from odoo import Command, models


class ApartmentPlugApartment(models.Model):
    _inherit = "apartmentplug.apartment"

    def action_create_invoice(self):
        self.ensure_one()
        self.env["account.move"].create(
            {
                "name": f"Invoice Test-{self.name}",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": f"{self.name} - Test",
                            "quantity": 1,
                            "price_unit": 100.0,
                            "account_id": 1,
                        }
                    )
                ],
            }
        )
        return super().action_create_invoice()
