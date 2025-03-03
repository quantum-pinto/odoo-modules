from odoo import fields, models
from odoo.tools.sql import column_exists, create_column


class AccountMove(models.Model):
    _inherit = "account.move"

    lag_days = fields.Integer(
        compute="_compute_lag_days",
        store=True,
    )

    def _auto_init(self):
        """Extend init.

        Create column for lag_days to avoid ORM compute during module upgrade/install.
        """
        if not column_exists(self.env.cr, "account_move", "lag_days"):
            create_column(self.env.cr, "account_move", "lag_days", "integer")
        return super()._auto_init()

    def _compute_lag_days(self):
        for record in self:
            if record.state == "posted" and record.is_invoice(include_receipts=True):
                payment_data = record._get_reconciled_info_JSON_values()
                lag_total = 0
                for payment_dict in payment_data:
                    payment_date = payment_dict.get("date")
                    payment_amount = payment_dict.get("amount")
                    if (
                        not record.invoice_date_due
                        and not payment_date
                        and not record.amount_total
                        and not payment_amount
                    ):
                        continue
                    days_diff = (payment_date - record.invoice_date_due).days
                    lag_total += days_diff * (payment_amount / record.amount_total)
                record.lag_days = int(lag_total)
            else:
                record.lag_days = 0

    def action_compute_lag_days(self):
        for record in self:
            record._compute_lag_days()
        return {"type": "ir.actions.act_window_close"}
