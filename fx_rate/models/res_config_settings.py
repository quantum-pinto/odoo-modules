import datetime
import logging

import requests
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


FX_RATE_PROVIDER_SELECTION = [
    ([], "bog", "Bank of Ghana"),
]

API_URL = "http://localhost:8000/api/v1/rates/"


class ResCompany(models.Model):
    _inherit = "res.company"

    fx_rate_interval_unit = fields.Selection(
        selection=[
            ("manually", "Manually"),
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
        ],
        default="manually",
        required=True,
        string="Interval Unit",
    )
    fx_rate_next_execution_date = fields.Date(string="Next Execution Date")

    fx_rate_service_provider = fields.Selection(
        selection=[
            (provider_code, desc)
            for dummy, provider_code, desc in FX_RATE_PROVIDER_SELECTION
        ],
        string="Service Provider",
        compute="_compute_fx_rate_service_provider",
        readonly=False,
        store=True,
    )

    @api.depends("country_id")
    def _compute_fx_rate_service_provider(self):
        code_providers = {
            country: provider_code
            for countries, provider_code, dummy in FX_RATE_PROVIDER_SELECTION
            for country in countries
        }
        for record in self:
            record.fx_rate_service_provider = code_providers.get(
                record.country_id.code, "bog"
            )

    def fetch_fx_rates(self):
        try:
            response = requests.get(API_URL, timeout=30)
            response.raise_for_status()
            data = response.json()
            if data:
                for rate in data[0]["rates"]:
                    currency = self.env["res.currency"].search(
                        [("name", "=", rate["currency_code"])], limit=1
                    )
                    if currency:
                        self.env["res.currency.rate"].create(
                            {
                                "currency_id": currency.id,
                                "rate": rate["mid_rate"],
                                "name": data[0]["date"],
                            }
                        )
                    else:
                        _logger.info("%s Not Found", rate["currency_code"])
            else:
                _logger.error("No rates found in response")
        except requests.exceptions.RequestException as e:
            _logger.error("Failed to fetch FX rates: %s", str(e))

    def fetch_new_fx_rates(self):
        """
        This method is used to update all currencies by fetching
        from the custom API.
        """
        try:
            self.fetch_fx_rates()
            return True
        except Exception as error:
            if self._context.get("suppress_errors"):
                _logger.warning(error)
                _logger.warning(
                    "Unable to fetch FX rates. The web service may be temporarily down."
                    "Please try again in a moment."
                )
                return False
            elif isinstance(error, UserError):
                raise error
            else:
                raise UserError(
                    _("The web service may be temporarily down. Please try again")
                ) from error

    @api.model
    def run_fetch_new_fx_rates(self):
        """This method is called from a cron job to update currency rates."""
        records = self.search(
            [
                ("fx_rate_next_execution_date", "<=", fields.Date.today()),
                ("parent_id", "=", False),
            ]
        )
        if records:
            to_update = self.env["res.company"]
            for record in records:
                if record.fx_rate_interval_unit == "daily":
                    next_update = relativedelta(days=+1)
                elif record.fx_rate_interval_unit == "weekly":
                    next_update = relativedelta(weeks=+1)
                elif record.fx_rate_interval_unit == "monthly":
                    next_update = relativedelta(months=+1)
                else:
                    record.fx_rate_next_execution_date = False
                    continue
                record.fx_rate_next_execution_date = datetime.date.today() + next_update
                to_update += record
            to_update.with_context(suppress_errors=True).fetch_new_fx_rates()


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    fx_rate_service_provider = fields.Selection(
        related="company_id.fx_rate_service_provider", readonly=False
    )
    fx_rate_interval_unit = fields.Selection(
        related="company_id.fx_rate_interval_unit", readonly=False
    )
    fx_rate_next_execution_date = fields.Date(
        related="company_id.fx_rate_next_execution_date", readonly=False
    )

    @api.onchange("fx_rate_interval_unit")
    def onchange_fx_rate_interval_unit(self):
        if self.company_id.fx_rate_next_execution_date:
            return
        if self.fx_rate_interval_unit == "daily":
            next_update = relativedelta(days=+1)
        elif self.fx_rate_interval_unit == "weekly":
            next_update = relativedelta(weeks=+1)
        elif self.fx_rate_interval_unit == "monthly":
            next_update = relativedelta(months=+1)
        else:
            self.fx_rate_next_execution_date = False
            return
        self.fx_rate_next_execution_date = datetime.date.today() + next_update

    def update_fx_rates_manually(self):
        self.ensure_one()
        self.company_id.fetch_new_fx_rates()
