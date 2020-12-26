odoo.define('satavan.product_items_order', function (require) {
    "use strict";
    
    var ajax = require('web.ajax');
    $(document).ready(function () {
        ajax.jsonRpc("/shop/cartcustom/create-order", 'call', {}).then(function (data) {
            console.log(data)
        })
    })
})