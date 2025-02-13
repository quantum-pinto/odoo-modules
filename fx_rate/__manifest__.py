{
    "name": "Fx Rate",
    "summary": "Fetch FX rates from an external API",
    "author": "Pinto",
    "website": "https://github.com/quantum-pinto/odoo-modules",
    "version": "17.0.1.0.0",
    "license": "Other proprietary",
    "category": "Accounting",
    "depends": [
        "base",
        "account",
    ],
    "data": [
        "views/res_config_settings_views.xml",
        "data/fx_rate_cron.xml",
    ],
    "application": True,
}
