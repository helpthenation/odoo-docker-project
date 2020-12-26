# coding: utf-8

import logging
import hashlib
import urllib
# import urllib2

# from urllib import urlencode
from urllib.parse import urlencode
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.http import request
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.queue_job.job import job


_logger = logging.getLogger(__name__)


class AcquirerVnpay(models.Model):
    _name = 'payment.acquirer'
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('vnpay', 'VN Pay')])
    vnpay_website_code = fields.Char('Website code', required_if_provider='vnpay', groups='base.group_user')
    vnpay_type = fields.Selection(selection=[
        ('InternationalCard', 'Thẻ quốc tế'),
        ('DomesticBank', 'Atm Nội địa'),
        ], string="Loại thanh toán", required_if_provider='vnpay')

    vnpay_hash_secret = fields.Char('Hash code', groups='base.group_user')

    environment = fields.Selection([
        ('test', 'Test'),
        ('prod', 'Production')], string='Environment',
        default='test', oldname='env', required=True)

    

    # Default payment fees
    fees_dom_fixed = fields.Float(default=1760)
    fees_dom_var = fields.Float(default=1.1)
    fees_int_fixed = fields.Float(default=1760)
    fees_int_var = fields.Float(default=1.1)


    # @api.multi
    def toggle_environment_value(self):
        prod = self.filtered(lambda acquirer: acquirer.environment == 'prod')
        prod.write({'environment': 'test'})
        (self-prod).write({'environment': 'prod'})



    def _get_feature_support(self):
        """Get advanced feature support by provider.

        Each provider should add its technical in the corresponding
        key for the following features:
            * fees: support payment fees computations
            * authorize: support authorizing payment (separates
                         authorization and capture)
            * tokenize: support saving payment data in a payment.tokenize
                        object
        """
        res = super(AcquirerVnpay, self)._get_feature_support()
        res['fees'].append('vnpay')
        res['authorize'].append('vnpay')
        return res

    @api.model
    def _vnpay_get_urls(self, environment):
        """ Paypal URLS """
        if environment == 'prod':
            return {
                'form_url': 'https://pay.vnpay.vn/vpcpay.html',
            }
        else:
            return {
                'form_url': 'http://sandbox.vnpayment.vn/paymentv2/vpcpay.html',
            }

    # @api.multi
    def vnpay_compute_fees(self, amount, currency_id, country_id):
        """ Compute fees.

            :param float amount: the amount to pay
            :param integer country_id: an ID of a res.country, or None. This is
                                       the customer's country, to be compared to
                                       the acquirer company country.
            :return float fees: computed fees
        """
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return fees

    def make_payment_url(self,data_query):
        inputData = sorted(data_query.items())
        queryString = ''
        hasData = ''
        seq = 0
        for key in inputData:
            if seq == 1:
                queryString = queryString + "&" + key + '=' + urlencode(inputData[key])
                hasData = hasData + "&" + str(key) + '=' + str(inputData[key])
            else:
                seq = 1
                queryString = key + '=' + urlencode(inputData[key])
                hasData = str(key) + '=' + str(val)
        data_hash = (self.vnpay_hash_secret + hasData).encode('utf-8')
        hashValue = hashlib.sha256(data_hash).hexdigest()
        return queryString + '&vnp_SecureHashType=SHA256&vnp_SecureHash=' + hashValue

    # @api.multi
    def vnpay_form_generate_values(self, values):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        tx_values = dict(values)

        reference_number = (values['reference'])
        data_query = {
            'vnp_Version': '2.0.0',
            'vnp_Command': 'pay',
            'vnp_OrderType': 'oldmc',
            'vnp_TmnCode': self.vnpay_website_code,
            'vnp_Amount' :  int(float(values['amount'])*100),
            'vnp_CreateDate' : datetime.now().strftime('%Y%m%d%H%M%S'),
            'vnp_CurrCode' : 'VND',
            'vnp_Locale': 'vn',
            'vnp_OrderInfo': 'Thanh toan don hang %s' % reference_number,
            'vnp_ReturnUrl':  base_url + '/payment/vnpay/dpn/',
            'vnp_TxnRef':  reference_number,
            'vnp_IpAddr': request.httprequest.remote_addr
        }

        plain_params = self.vnpay_hash_secret
        # for key in sorted(data_query.iterkeys()):
        for key in sorted(data_query):
            plain_params += '%s' % ((data_query[key]))

        data_hash = hashlib.md5(plain_params.encode('utf-8')).hexdigest()
        data_query.update({
            'vnp_SecureHashType': 'MD5',
            'vnp_SecureHash': data_hash
        })
        tx_values.update(data_query)

        return tx_values

    # @api.multi
    def vnpay_get_form_action_url(self):
        return self._vnpay_get_urls(self.environment)['form_url']

class TxVnPay(models.Model):
    _inherit = 'payment.transaction'

    # paypal_txn_type = fields.Char('Transaction type')

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    @api.model
    def _vnpay_form_get_tx_from_data(self, data):
        _logger.info('================_vnpay_form_get_tx_from_data')
        _logger.debug(data)

        reference = data.get('vnp_TxnRef')
        
        if not reference:
            error_msg = _('VNpay: received data with missing reference (%s)') % (reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        
        if not txs or len(txs) > 1:
            error_msg = 'VNpay: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    def __md5(self, input):
        byteInput = input.encode('utf-8')
        return hashlib.md5(byteInput).hexdigest()

    # @api.multi
    def _vnpay_form_get_invalid_parameters(self, data):
        _logger.info('=====_vnpay_form_get_invalid_parameters')
        invalid_parameters = []
        _logger.info('Received a notification from VN PAY with Data %s', data.get('data'))
        return invalid_parameters

    # @api.multi
    def _vnpay_form_validate(self, data):
        _logger.info('======_vnpay_form_validate')
        try:
            status = data.get('vnp_ResponseCode')
        except:
            status = -1

        res = {
            'acquirer_reference': '%s-%s-%s' % (data.get('vnp_TransactionNo', ''),
                                                data.get('vnp_BankTranNo', ''),
                                                data.get('vnp_BankCode', ''))
            # 'paypal_txn_type': data.get('payment_type'),
        }
        if status == '00':
            if self.state == 'done':
                _logger.info('Transaction already confirmed')
                return self
 
            _logger.info('Validated VNpay payment for tx %s: set as done' % (self.reference))
            validate_time = datetime.strptime(data.get('vnp_PayDate', fields.datetime.now()),'%Y%m%d%H%M%S')
            validate_time = validate_time - timedelta(hours=7)
            
            _new_state = 'authorized' # TODO: or pending?
            if self.state in ('authorized', 'pending'):
                _new_state = 'done'
            res.update(state = _new_state, date_validate = validate_time, state_message = data)
            _logger.info('status = %s has updated' % _new_state)
        else:
            if status == '24':
                error = 'Payment is cancel for VN payment %s: %s, set as error' % (self.reference, status)
                _logger.error(error)
            else:
                error = 'Received unrecognized status for VN payment %s: %s, set as error' % (self.reference, status)
                _logger.error(error)
            res.update(state = 'error', state_message = data)
        return self.write(res)

    # @api.multi
    @job
    def run_job_form_feedback_vnpay(self, post):
        self.sudo().form_feedback(post, 'vnpay')
