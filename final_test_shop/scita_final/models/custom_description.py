# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    description_detail_web = fields.Html()
    guarantee = fields.Selection([
        ('One', '1 năm'),
        ('Two', '2 năm')],
        default="One",
        string="Guarantee",)

    maintenance = fields.Selection([
        ('One', '1 năm'),
        ('Two', '2 năm'),
        ('forever', 'Vĩnh viễn')],
        default="One",
        string="Guarantee",)


class ProductSnippetConfiguration(models.Model):
    _inherit = "product.snippet.configuration"

    url = fields.Char(string="url", default="#")
