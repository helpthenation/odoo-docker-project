odoo.define('satavan.search', function (require) {
    "use strict";

    $(document).ready(function () {
        $('#search_menu_order').on('keyup', function() {
            const search = convertToEnglish($(this).val()).toLowerCase();

            toggleProduct(search);
        })

        const toggleProduct = search => {
            $('.devvn_term_item .box-items').filter(function() {
                const productName = convertToEnglish($(this).find('.devvn_product_name').html()).toLowerCase();

                $(this).toggle(productName.indexOf(search) !== -1);

                $(this).closest('.devvn_section_category').toggle( isHasProductVisible( $(this) ) );
            });
        }

        const isHasProductVisible = target => {
            let productVisible = false;

            target.closest('.devvn_section_category').find('.box-items').each(function() {
                productVisible = $(this).css('display') == 'block' || productVisible;
            })

            return productVisible;
        }

    })
})