# -*- coding: utf-8 -*-

from odoo import http, SUPERUSER_ID
from odoo.http import request
import time
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.translate import _
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import QueryURL
from odoo.addons.website_sale.controllers import main
from odoo.addons.website.controllers.main import Website
from odoo.addons.web_editor.controllers.main import Web_Editor
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website.models.ir_http import sitemap_qs2dom
# from odoo.addons.sale.controllers.product_configurator import ProductConfiguratorController
import json
from lxml import etree, html
import math
import os
import base64
import uuid
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo import http

main.PPG = 10000000
PPG=main.PPG

# class WebsiteSale(ProductConfiguratorController):


class WebsiteSale(WebsiteSale):
    #get variant
    def get_attribute_value_ids(self, product):
        quantity = product._context.get('quantity') or 1
        product = product.with_context(quantity=quantity)
        visible_attrs_ids = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id').ids
        attribute_value_ids = []
        for variant in product.product_variant_ids:
            visible_attribute_ids = [v.product_attribute_value_id.id for v in variant.product_template_attribute_value_ids if
                                     v.attribute_id.id in visible_attrs_ids]
            attribute_value_ids.append([variant.id, visible_attribute_ids])
            print(attribute_value_ids)
        return attribute_value_ids

    @http.route(
        ['/page/product_brands'],
        type='http',
        auth='public',
        website=True)
    def product_brands(self, **post):
        cr, context, pool = (request.cr,
                             request.context,
                             request.registry)
        b_obj = request.env['product.brand']
        domain = []
        if post.get('search'):
            domain += [('name', 'ilike', post.get('search'))]
        brand_ids = b_obj.search(domain)

        keep = QueryURL('/page/product_brands', brand_id=[])
        values = {'brand_rec': brand_ids,
                  'keep': keep}
        if post.get('search'):
            values.update({'search': post.get('search')})
        return request.render(
            'alan_final.product_brands',
            values)

    def sitemap_shop(env, rule, qs):
        if not qs or qs.lower() in '/shop':
            yield {'loc': '/shop'}

        Category = env['product.public.category']
        dom = sitemap_qs2dom(qs, '/shop/category', Category._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for cat in Category.search(dom):
            loc = '/shop/category/%s' % slug(cat)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True, sitemap=sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = 1000000000000000

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list,
                        order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].with_context(bin_size=True)

        search_product = Product.search(domain, order=self._get_search_order(post))
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search(
                [('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']
        products = search_product[offset: offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)

    @http.route(['/shop/cart/clean_cart'], type='json', auth="public", website=True)
    def clean_cart(self, type_id=None):
        order = request.website.sale_get_order()
        request.website.sale_reset()
        if order:
            order.sudo().unlink();
        return {}

    @http.route(['/shop/product/update_cart_popup'], type='http', auth="public", website=True)
    def update_cart_popup(self):
        order = request.website.sale_get_order()
        return request.render("alan_final.product_cart", {'website':request.website})
        
    @http.route(['/shop/productCustomTest/<product>'], type='json', auth="public", website=True)
    def productCustomTest(self, product, category='', search='', **kwargs):
        product_id = request.env['product.template'].browse(int(product)).exists()
        pricelist_id = request.website.get_current_pricelist().id
        pricelist = product_id.with_context(pricelist=pricelist_id).price
        product_variant_price = request.env['product.template.attribute.value'].sudo().search([('product_tmpl_id', '=', product_id.id)])
        product_variant = []
        for item in product_id:
            variant_ids = []
            for variant_id in item.attribute_line_ids:
                variant_ids.append('attribute' + '-' + str(item.id) + '-' + str(variant_id.attribute_id.id))
                for value in variant_id.value_ids:
                    for price_value in product_variant_price:
                        if value.id == price_value.product_attribute_value_id.id:
                            product_variant.append({
                                    'id': item.id,
                                    'name': variant_id.attribute_id.name,
                                    'name_attribute': value.name,
                                    'value_id': value.id,
                                    'price_variant': price_value.price_extra,
                                    'variant_ids': variant_ids
                                })
        values = {
            'product_id': int(product_id.product_variant_ids[0]) if len(product_id.product_variant_ids) == 1 else '0',
            'name': product_id.name,
            'category': category,
            'pricelist': pricelist,
            'product_variant': product_variant,
            'get_attribute_value_ids': self.get_attribute_value_ids(product_id),
            'data_attribute_value_ids': product_id.product_variant_ids.ids,
        }
        return json.dumps(values)


    def _filter_attributes(self, **kw):
        return {k: v for k, v in kw.items() if "attribute" in k}

    # @http.route(['/sale/create_product_variant'], type='json', auth="user", methods=['POST'])
    # def create_product_variant(self, product_template_id, product_template_attribute_value_ids, **kwargs):
    #     print("asdsa")
    #     if not product_template_id:
    #         return request.env['product.template'].browse(int(product_template_id)).create_product_variant(product_template_attribute_value_ids)



    @http.route(['/shop/cartcustomShop/update'], type='json', auth="public", methods=['GET', 'POST'], website=True, csrf=False)
    def cart_update_custom_shop(self, product_id, add_qty=1, set_qty=0, **kw):
        print('abc')
        product_id = int(product_id)
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)
        value = sale_order._cart_update(product_id=product_id, add_qty=add_qty, set_qty=set_qty)
        for sa in sale_order.mapped('website_order_line'):
            value['name_sale_order'] = sa.product_id.with_context(display_default_code=False).display_name
            value['price_unit'] = sa.price_unit
        value['cart_quantity'] = sale_order.cart_quantity
        value['product_uom_qty'] = value['quantity']
        value['product_id'] = product_id
        value['amount_total'] = sale_order.amount_total
        return value

    @http.route(['/shop/cartcustom/create-order'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def create_order_custom(self):
        user_current = http.request.env.context.get('uid') 
        user = request.env['res.users'].browse(user_current)
        partner = user.partner_id.id
        sale_order = request.website.sale_get_order(force_create=True)
        if partner == sale_order.partner_id.id:
            return sale_order



    @http.route(['/shop/cartTest/update'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_test(self, product_id, add_qty=1, set_qty=0, **kw):
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)
        value = sale_order._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            attributes=self._filter_attributes(**kw),
        )
        value['alan_final.product_items'] = request.env['ir.ui.view'].render_template("alan_final.product_items", {
            'website_sale_order': sale_order
        })
        return value

    @http.route(['/shop/cartCustom'], type='http', auth="public", website=True)
    def cartcustom(self, access_token=None, revive='', **post):
        """
        Main cart management + abandoned cart revival
        access_token: Abandoned cart SO access token
        revive: Revival method when abandoned cart. Can be 'merge' or 'squash'
        """
        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()
        values = {}
        if access_token:
            abandoned_order = request.env['sale.order'].sudo().search([('access_token', '=', access_token)], limit=1)
            if not abandoned_order:  # wrong token (or SO has been deleted)
                return request.render('website.404')
            if abandoned_order.state != 'draft':  # abandoned cart already finished
                values.update({'abandoned_proceed': True})
            elif revive == 'squash' or (revive == 'merge' and not request.session['sale_order_id']):  # restore old cart or merge with unexistant
                request.session['sale_order_id'] = abandoned_order.id
                return request.redirect('/shop/cartCustom')
            elif revive == 'merge':
                abandoned_order.order_line.write({'order_id': request.session['sale_order_id']})
                abandoned_order.action_cancel()
            elif abandoned_order.id != request.session['sale_order_id']:  # abandoned cart found, user have to choose what to do
                values.update({'access_token': abandoned_order.access_token})

        if order:
            from_currency = order.company_id.currency_id
            to_currency = order.pricelist_id.currency_id
            compute_currency = lambda price: from_currency.compute(price, to_currency)
        else:
            compute_currency = lambda price: price

        values.update({
            'website_sale_order': order,
            'compute_currency': compute_currency,
            'suggested_products': [],
        })
        if order:
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()

        if post.get('type') == 'popover':
            # force no-cache so IE11 doesn't cache this XHR
            return request.render("website_sale.cart_popover", values, headers={'Cache-Control': 'no-cache'})

        return request.render("alan_final.cart_custom", values)   


    @http.route(['/shop/cart_custom/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        """This route is called when changing quantity from the cart or adding
        a product from the wishlist."""
        order = request.website.sale_get_order(force_create=1)
        if order.state != 'draft':
            request.website.sale_reset()
            return {}

        value = order._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty)

        if not order.cart_quantity:
            request.website.sale_reset()
            return value

        for sa in order.mapped('website_order_line'):
            value['name_sale_order'] = sa.product_id.with_context(display_default_code=False).display_name
        order = request.website.sale_get_order()
        value['cart_quantity'] = order.cart_quantity
        value['product_uom_qty'] = value['quantity']
        value['product_id'] = product_id
        value['amount_total'] = order.amount_total

        if not display:
            return value

        # value['website_sale.cart_lines'] = request.env['ir.ui.view'].render_template("website_sale.cart_lines", {
        #     'website_sale_order': order,
        #     'date': fields.Date.today(),
        #     'suggested_products': order._cart_accessories()
        # })
        # value['website_sale.short_cart_summary'] = request.env['ir.ui.view'].render_template("website_sale.short_cart_summary", {
        #     'website_sale_order': order,
        # })
        return value


    #checkout and payment

    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            return request.redirect('/shop/address')

        for f in self._get_mandatory_billing_fields():
            if not order.partner_id[f]:
                return request.redirect('/shop/address?partner_id=%d' % order.partner_id.id)

        values = self.checkout_values(**post)

        values.update({'website_sale_order': order})

        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'
        return request.render("website_sale.checkout", values)







