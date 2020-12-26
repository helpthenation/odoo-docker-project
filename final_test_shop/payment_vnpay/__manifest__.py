# -*- coding: utf-8 -*-

{
    'name': 'VNPay Payment Acquirer',
    'category': 'Accounting',
    'summary': 'Payment Acquirer: VNPay',
    'website': 'http://tictag.vn',
    'version': '1.0',
    'description': """VNPay Payment Acquirer""",
    'depends': [
        'payment',
        'connector'
    ],
    'data': [
        'views/payment_views.xml',
        # 'views/payment_templates.xml',
        'views/payment_templates_fixed.xml',
        'data/payment_acquirer_data.xml',
    ],
    'installable': True,
}
