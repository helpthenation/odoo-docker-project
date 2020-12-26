# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Fianal scita',
    'version': '1.0',
    'category': 'Website/Website',
    'description': """
Allows you to add delivery methods in sale orders and picking.
==============================================================

You can define your own carrier for prices. When creating
invoices from picking, the system is able to add and compute the shipping line.
""",
    'depends': ['theme_scita', 'alan_final', 'payment_vnpay'],
    'data': [
        'views/custom_description.xml',
        'views/assets.xml',
        'views/address.xml',
    ],
    'demo': ['data/delivery_demo.xml'],
    'installable': True,
}
