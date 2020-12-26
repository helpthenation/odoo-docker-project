odoo.define('theme_watch.clean', function (require) {
"use strict";

var ajax = require('web.ajax');
   $(document).ready(function ()
  {
  $("body").on('click','.remove_cart_shop',function (ev){
        ajax.jsonRpc("/shop/cart/clean_cart", 'call', {}).then(function (data){
            swal({
            title: "Bạn có chắc chắn muốn xóa tất cả?",
            icon: "warning",
            dangerMode: true,
        })
            .then((willDelete) => {
                if (willDelete) {
                    swal("Bạn đã xóa thành công", {
                        icon: "success",
                        buttons:  renderCartEmpty(),
                    });
                } else {
                    swal("Bạn đã xóa thất bại");
                }
            });
            ajax.jsonRpc("/shop/cartcustom/create-order", 'call', {}).then(function (data) {
                console.log(data)
            })
        });
        if($('.total_0 .devvn_sidebar_entry').length == 0){
            $('.navbar-collapse .my_cart_quantity').remove();
        }
        return false;
    });
});
});