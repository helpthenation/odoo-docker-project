# -*- coding: utf-8 -*-

import json
import logging
import pprint
# import urllib
import werkzeug
from urllib.parse import quote as quote
from datetime import datetime
import hashlib

from odoo import http
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class VNpayController(http.Controller):

    @http.route('/payment/vnpay/dpn/', type='http', auth='none', csrf=False)
    def vnpay_dpn(self,**post):
        try:
            _logger.info('=============== DPN form_feedback with post data')
            _logger.info(pprint.pformat(post))  # debug
            check_confirm = self.check_confirm_invalid(post)
            code = check_confirm.get('code')
            if code == 200:
                status = post.get('vnp_ResponseCode')
                vnp_TransactionNo = post.get('vnp_TransactionNo')
                _logger.debug('--vnp_TransactionNo = %s' % vnp_TransactionNo)

                if status == '24':
                    _logger.info('===Payment Cancelled')

                    if vnp_TransactionNo != 0:
                        # đã có trans trên vnpay 
                        _logger.info('===Payment trans existed in vnpay')
                        request.env['payment.transaction'].sudo().form_feedback(post, 'vnpay')
                    link_error_msg = '/shop/payment_gateway/error/?error=%s' % (status)
                    return werkzeug.utils.redirect(link_error_msg)
                else:
                    _logger.info('====Payment is validating...')
                    result = request.env['payment.transaction'].sudo().form_feedback(post, 'vnpay')
                    _logger.debug(result)
                    return werkzeug.utils.redirect('/shop/payment/validate')
            else:
                _logger.error('Code: %s' % code)
                link_error_msg = '/shop/payment_gateway/error/?error=%s' % (code)
        except Exception as e:
            _logger.error('Exception:')
            _logger.error(e)
            link_error_msg = '/shop/payment_gateway/error/?error=%s' % (e)
            return werkzeug.utils.redirect(link_error_msg)
        
    @http.route('/payment/vnpay/ipn/', type='http', auth='none', csrf=False)
    def vnpay_ipn(self,**post):
        _logger.info('================= IPN form_feedback with post data')
        _logger.info(pprint.pformat(post))  # debug
        try:
            check_confirm = self.check_confirm_invalid(post)
            if check_confirm.get('code') == 200:
                request.env['payment.transaction'].sudo().with_delay(eta=300).run_job_form_feedback_vnpay(post)
                # request.env['payment.transaction'].sudo().form_feedback(post, 'vnpay')
                return json.dumps({'RspCode': '00', 'Message': 'Confirm Success'})
            else:
                return json.dumps({
                    'RspCode': check_confirm.get('code'),
                    'Message': check_confirm.get('message')
                })
        except Exception as e:
            _logger.error('Exception:')
            _logger.error(e)
            return json.dumps({
                'RspCode': '99',
                'Message': u'IPN không thể xử lý hoặc có exception xảy ra'
            })

    def check_confirm_invalid(self, data):
        _logger.info('==========check_confirm_invalid')
        reference = data.get('vnp_TxnRef', False)
        if not reference:
            error_msg = 'check_confirm_invalid: received data with missing reference (%s)' % (reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use txn_id ?
        txs = request.env['payment.transaction'].sudo().search([('reference', '=', reference)])

        if not txs or len(txs) > 1:
            error_msg = 'check_confirm_invalid: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
                _logger.error(error_msg)
                return {'code': '01', 'message': u'Không tìm thấy giao dịch'}
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        acquirer = txs.acquirer_id
        secret_key = acquirer.vnpay_hash_secret
        if not self.check_sum(secret_key, data):
            error_msg = 'check_confirm_invalid: Check sum is FAIL'
            _logger.error(error_msg)
            return {'code': '97', 'message': u'Sai Checksum'}

        if txs.state == 'done':
            return {'code': '02', 'message': u'Giao dịch đã được cập nhật trạng thái thanh toán'}

        return {'code': 200, 'message': 'Confirm Success'}

    def check_sum(self, secret_key, data):
        vnp_SecureHash = data.get('vnp_SecureHash')
        # Remove hash params
        if 'vnp_SecureHash' in data.keys():
            data.pop('vnp_SecureHash')

        if 'vnp_SecureHashType' in data.keys():
            data.pop('vnp_SecureHashType')

        inputData = sorted(data.items())
        hasData = ''
        seq = 0

        for key, val in inputData:
            if str(key).startswith('vnp_'):
                if seq == 1:
                    hasData = hasData + "&" + str(key) + '=' + str(val)
                else:
                    seq = 1
                    hasData = str(key) + '=' + str(val)
        hashValue = self.__md5(secret_key + hasData)
        return vnp_SecureHash == hashValue

    def __md5(self, input):
        byteInput = input.encode('utf-8')
        return hashlib.md5(byteInput).hexdigest()

    @http.route('/payment/vnpay/render_pay', type='http', auth='public', website=True)
    def check_vnpay_type(self,**post):
        _logger.info("===============Render data to pay===========")
        _logger.debug(post)
        # Cần kiểm tra luôn trường hợp tx đã thanh toán
        ref =  post.get('vnp_TxnRef')
        if not ref:
            _logger.error('Error code 1: no ref')
            return werkzeug.utils.redirect('/shop/payment?payment_error=1')

        tx = request.env['payment.transaction'].sudo().search([('reference','=',ref)])
        if not tx or not tx.sale_order_ids:
            _logger.error('Error code 2: No tx or tx do not have SO')
            return werkzeug.utils.redirect('/shop/payment?payment_error=2')

        so = tx.sale_order_ids[0]
        # TODO: so.payment_acquirer_id not exist in v12
        # if so.payment_acquirer_id.id != tx.acquirer_id.id:
            # _logger.error('Error code 3: TX and SO do not same Acquirer %d != %d' % (so.payment_acquirer_id.id, tx.acquirer_id.id))
            # return werkzeug.utils.redirect('/shop/payment?payment_error=3')

        pay_type = tx.acquirer_id.vnpay_type

        post['show_amount'] = so.amount_total
        post['show_des'] = u'Thanh toán đơn hàng %s' % so.name
        # return request.render("payment_vnpay.vnpay_international_card",{})
        if pay_type == 'InternationalCard':
            return request.render("payment_vnpay.vnpay_international_card", post)
        if pay_type == 'DomesticBank':
            return request.render("payment_vnpay.vnpay_domesticbank", post)

    @http.route('/payment/vnpay/commit_pay', type='http', auth='none')
    def vnpay_render_form(self,**post):
        _logger.info("====================Commit data to pay==============")
        _logger.debug(post)
        # Cần kiểm tra luôn trường hợp tx đã thanh toán
        ref = post.get('vnp_TxnRef')
        bankCode = post.get('vnp_BankCode')
        if not ref:
            _logger.error('Error code 1: no ref')
            return werkzeug.utils.redirect('/shop/payment?payment_error=1')

        tx = request.env['payment.transaction'].sudo().search([('reference', '=', ref)])
        if not tx or not tx.sale_order_ids:
            _logger.error('Error code 2: No tx or tx do not have SO')
            return werkzeug.utils.redirect('/shop/payment?payment_error=2')

        so = tx.sale_order_ids[0]
        # if so.payment_acquirer_id.id != tx.acquirer_id.id:
            # _logger.error('Error code 3: TX and SO do not same Acquirer %d != %d' % (so.payment_acquirer_id.id,tx.acquirer_id.id))
            # return werkzeug.utils.redirect('/shop/payment?payment_error=3')
        url = self.get_payment_url(tx, bankCode)
        return werkzeug.utils.redirect(url)

    def get_payment_url(self, tx, bankCode):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        acquirer = tx.acquirer_id
        secret_key  = acquirer.vnpay_hash_secret
        data_query = {
            'vnp_Version': '2.0.0',
            'vnp_Command': 'pay',
            'vnp_OrderType': 'oldmc',
            'vnp_TmnCode': acquirer.vnpay_website_code,
            'vnp_Amount' : int(float(tx.sale_order_ids[0].amount_total)*100),
            'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
            'vnp_CurrCode': 'VND',
            'vnp_Locale': 'vn',
            'vnp_OrderInfo': 'Thanh toan don hang %s' % tx.reference,
            'vnp_ReturnUrl': base_url + '/payment/vnpay/dpn/',
            'vnp_TxnRef': tx.reference,
            'vnp_IpAddr': request.httprequest.remote_addr,
            'vnp_BankCode': bankCode
        }

        inputData = sorted(data_query.items())
        queryString = ''
        hasData = ''
        seq = 0
        for key, val in inputData:
            if seq == 1:
                queryString += "&" + key + '=' + quote(str(val))
                hasData += "&" + str(key) + '=' + str(val)
            else:
                seq = 1
                queryString = key + '=' + quote(str(val))
                hasData = str(key) + '=' + str(val)

        hashValue = hashlib.md5((secret_key + hasData).encode('utf-8')).hexdigest()
        # return 'http://sandbox.vnpayment.vn/paymentv2/vpcpay.html' + "?" + queryString + '&vnp_SecureHashType=MD5&vnp_SecureHash=' + hashValue
        return acquirer.vnpay_get_form_action_url() + "?" + queryString + '&vnp_SecureHashType=MD5&vnp_SecureHash=' + hashValue
