{
    "name": "Letter Sign",
    "summary": "Integrate e-signature in letter",
    "author": "Pinto",
    "website": "https://github.com/quantum-pinto/odoo-modules",
    "version": "17.0.1.0.2",
    "license": "Other proprietary",
    "category": "Uncategorized",
    "depends": [
        "base",
        "letter",
        "sign",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/letter_letter.xml",
        "views/letter_menus.xml",
        "wizard/sign_send_request_views.xml",
    ],
    "application": True,
    "installable": True,
}
