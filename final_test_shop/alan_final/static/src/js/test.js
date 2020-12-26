/* /web/static/lib/bootstrap/js/modal.js defined in bundle 'web.assets_common' */
+
function($) {
    'use strict';
    var Modal = function(element, options) {
        this.options = options
        this.$body = $(document.body)
        this.$element = $(element)
        if (this.options.remote) {
            this.$element.find('.modal-product').load(this.options.remote, $.proxy(function() {
                this.$element
            }, this))
        }
    }
    Modal.VERSION = '3.3.4'
    Modal.TRANSITION_DURATION = 0.2
    Modal.BACKDROP_TRANSITION_DURATION = 0.2
    Modal.DEFAULTS = {
        backdrop: true,
        keyboard: true,
        show: true
    }

    function Plugin(option, _relatedTarget) {

        return this.each(function() {
            var $this = $(this)
            var data = $this.data('bs.modal')
            var options = $.extend({}, Modal.DEFAULTS,  Modal.VERSION, Modal.TRANSITION_DURATION ,  Modal.BACKDROP_TRANSITION_DURATION, $this.data(), typeof option == 'object' && option)
            console.log(options)
            if (!data) $this.data('bs.modal', (data = new Modal(this, options)))
        })
    }
    setTimeout(function() { 
       $(document).on('click.bs.modal.data-api','[data-target="#exampleModalCenter1"]', function(e) {
        $('.modal-product').html(``)
        var $this = $(this) 
        var href = window.location.origin + $this.attr('href')
        var $target = $($this.attr('data-target') || (href && href.replace(/.*(?=#[^\s]+$)/, '')))
        var option = $target.data('bs.modal') ? $target : $.extend({
            remote: !/#/.test(href) && href
        }, $target.data(), $this.data())
        Plugin.call($target, option, this)
        
       
        })
    }, 1)
    const getPrice = () => {
        const plus = parseInt($('.devvn_option_name input:checked').closest('.js_attribute_value').find('.oe_currency_value').html()) || 0;
        const origin = parseInt($('.devvn_prd_price').html());

        return origin+plus;
    }

    const renderTotal = () => {
        const quantity = $('.devvn_boxvalid .quantity').val();
        const price = getPrice();
        const total = quantity * price;

        $('.total_price_1').html(total);
    }


    $('.js_add_cart_json').unbind('click').click(function() {
        setTimeout(() => {
            renderTotal();
        }, 100)
    })

    $('.js_variant_change').click(function() {
        $('.js_variant_change').attr('checked', false);
        $(this).prop('checked', true);
        renderTotal();
    })

    $('.js_variant_change:first').trigger('click');
    
}(jQuery);;

