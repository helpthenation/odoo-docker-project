odoo.define('satavan.product_items', function (require) {
    "use strict";
    
    var ajax = require('web.ajax');
       $(document).ready(function () {
            /* POPULAR LOADER */

            (function () {
              renderTemplateCart();
            })();

            /* POPULAR LOADER */


            /* POPUP DETAIL */

            const formatOptions = data => {
              const listData = [];
              
              data.forEach(element => {
                if(typeof listData[element.name] === 'undefined') {
                  listData[element.name] = []
                }

                listData[element.name].push(element);
              })

              return listData;
            }

            const renderOptions = data => {
              const listData = formatOptions(data.product_variant);

              for (const [title, elements] of Object.entries(listData)) {
                pushTitle(title);
                pushOptions(elements)
                setEventCheckbox(data.get_attribute_value_ids);
                triggerOption();
              }
            }

            const pushTitle = title => {
              $('.devvn_popup_content .devvn_option_name').append(
                `<span class="product_attribute">${title}</span>`
              )
            }

            const pushOptions = elements => {
              const templateOptions = fetchTemplateOptions(elements);
              $('.devvn_popup_content .devvn_option_name').append(templateOptions)
            }

            const fetchTemplateOptions = elements => {
              let options = '';

              if(elements.length) {
                options += '<ul class="list-unstyled block-option" style="list-style-type: none;margin: 0;padding: 0;overflow: hidden;">';

                elements.forEach(element => {
                  options += fetchTemplateOption(element);
                })

                options += '</ul>'
              }

              return options;
            }

            const fetchTemplateOption = element => {
              let option = `
                <li class="form-group js_attribute_value" style="margin: 0; padding: 5px;">
                  <label class="control-label" style="margin: 0 20px;">
                    <input type="checkbox" class="js_variant_change" name="${element.variant_ids[0]}" value="${element.value_id}">
                    <span>${element.name_attribute}</span>
                    <span class="add_price_plus">
                      +
                    <span style="white-space: nowrap;"><span class="oe_currency_value">${element.price_variant}</span>&nbsp;₫</span></span>
                  </label>
                </li>
              `;

              return option;
            }

            const setEventCheckbox = listAttr => {
              $('.js_variant_change').unbind('click').click(function() {
                $(this).closest('ul').find('.js_variant_change').prop('checked', false);
                $(this).prop('checked', true);

                let valueChecked = getValueAllChecked();
                let product_id = getIdProduct(listAttr, valueChecked);

                $('#product_id').val(product_id);

                renderTotal();
              })

            }

            const getValueAllChecked = () => {
              const result = [];

               $(".js_variant_change:input[type=checkbox]:checked").each(function(){
                  result.push($(this).val());
              });

              return result;
            }

            const getIdProduct = (listAttr, array_ids) => {
              let product_id = 0;

              listAttr.forEach(row => {
                if(typeof row[1] !== 'undefined') {
                    console.log(row)
                  if(row[1].length === 1 && row[1][0].toString() === array_ids[0].toString()) {
                    product_id = row[0] || product_id;
                  } else if(row[1].toString() === array_ids.toString()) {
                    product_id = row[0] || product_id;
                  }

                }
              })

              return product_id;
            }


            const triggerOption = () => {
              $('.block-option').each(function() {
               $(this).find('.js_variant_change:first').trigger('click');
              })
            }

            const setNamePopup = (data, image) => {
              $('.devvn_prd_title').html(data.name);
              $('.devvn_prd_price').html(data.pricelist);
              $('.total_price_1').html(data.pricelist);
              $('.devvn_prd_thumb').attr('src', image);
              $('#product_id').val(data.product_id);
              $('.devvn_popup_content .devvn_option_name').html('');
            }

            const setEventSubmit = () => {
              $('.modal-content #add_to_cart1').unbind('click').click(async function (event) {
                event.preventDefault();
                const response = await addToCart();

                response.product_info = {};
                response.product_info.image = $('.devvn_prd_thumb').attr('src');
                renderToCart(response);

                $('#exampleModalCenter').modal('hide');

                setEventRemoveItem();
              })
            }

            const addToCart = () => {
              const product_id = parseInt($('#product_id').val());
              const add_qty = parseInt($('.css_quantity input[name="add_qty"]').val());
              const set_qty = 0;
              console.log("aaaaaaaaaaaaaaaaaaaaaaaaaaaa")

              return new Promise(resolve => {
                ajax.jsonRpc("/shop/cartcustomShop/update", 'call', { product_id, add_qty, set_qty }).then(resolve)
              })
            }

            const getPrice = () => {
                let plus = 0;

                $('.devvn_option_name input:checked').each(function() {
                  plus += parseFloat($(this).closest('.js_attribute_value').find('.oe_currency_value').html());
                })

                const origin = parseFloat($('.devvn_prd_price').html());

                return origin+plus;
            }

            const renderTotal = () => {
                const quantity = $('.devvn_boxvalid .quantity').val();
                const price = getPrice();
                const total = quantity * price;

                $('.total_price_1').html(total);
            }


            $('.js_add_cart_json_custom').unbind('click').click(function() {
                setTimeout(() => {
                    renderTotal();
                }, 100)
            })

            /* POPUP DETAIL */


            /* CART DESKTOP */

            const renderToCart = response => {
              const target = $('#devvn_sidebar_onload .coupon_mobile');

              renderCartNotEmpty();

              renderBodyCart(response);

              renderFooterCart(response);

              updateNavCartMobile(response);

              updateIconQuantityHeader(getTotalQuantity());
            }

            const renderBodyCart = (response) => isExistItem(response) ? updateItemBodyCart(response) : addItemBodyCart(response);

            const isExistItem = (response) => $('.devvn_sidebar_entry[data-product-cart="'+response.product_id+'"]').length;

            const updateItemBodyCart = response => {
              const target = $('.devvn_sidebar_entry[data-product-cart="'+response.product_id+'"]');

              const quantityUpdate = parseInt(response.quantity);

              target.find('.js_quantity').val(quantityUpdate);
            }

            const addItemBodyCart = response => {
              const { product_info } = response;

              const tartgetDesktop = $('#devvn_sidebar_onload .coupon_mobile .total_0');
              const tartgetMobile = $('.modal-mobile .coupon_mobile .total_0');

              const template = `
<!--                    <script type="text/javascript"  src="/alan_final/static/src/js/cart_custom_13.js"></script>-->
                  <div class="devvn_sidebar_entry oe_website_sale" data-id="1131100" data-product-cart="${response.product_id}">
                   <div id="cart_products" class="devvn_item cart_items">
                      <div class="devvn_clear devvn_cart_item_left td-qty">
                         <div class="devvn_cart_item_qty css_quantity input-group mx-auto shop_cart_quanty">
                            <div class="replace_coupon">
                                   <a t-attf-href="#" class="js_add_cart_json_custom">
                                  <span class="devvn_plus_square devvn_square devvn_ajax_btn_plus">
                                     <i class="fa fa-minus change_data"/>
                                  </span>
                               </a>
                               <input style="border-radius: 100px; width: 25px; height: 25px; min-width: 0px !important" type="text" class="js_quantity form-control quantity my_cart_quantity devvn_ajax_valid_input" data-line-id="${response.line_id}" data-product-id="${response.product_id}" value="${response.quantity}" />
                               <a t-attf-href="#" class="float_left js_add_cart_json_custom">
                                  <span class="devvn_plus_square devvn_square devvn_ajax_btn_plus">
                                     <i class="fa fa-plus" />
                                  </span>
                               </a>
                            </div>
                         </div>
                         <div class="devvn_cart_item_infor" style="padding-left: 10px;">
                            <span class="devvn_sidebar_title"> 
                                <span class="h6 title_mobile">${response.name_sale_order}</span>
                            </span>
                            <div class="devvn_option">
                               <span><img src="${product_info.image}" class="img img-responsive image-card"></span>
                            </div>
                         </div>
                      </div>
                      <div class="cpptdev_sidebar_price devvn_clear oe_cart_123">
                            <span class="title_mobile">${response.price_unit}&nbsp;</span>
                            <a href="#" class="js_delete_product_shop no-decoration" data-oe-id="1591"><i class="fa fa-trash-o"></i>&nbsp;</a>
                      </div>
    
                   </div>
                </div>
              `;

              tartgetDesktop.append(template);
              tartgetMobile.append(template);
              ajax.jsonRpc("/shop/cartcustom/create-order", 'call', {}).then(function (data) {
                console.log(data)
              })
            }

            const renderFooterCart = response => {
              updateTotalQuantity();
              
              updateTotalPrice(response.amount_total);
            }

            const getTotalQuantity = () => {
              let totalQuantity = 0;

              $('#remove_cart_desktop .devvn_cart_item_qty .devvn_ajax_valid_input').each(function(){
                totalQuantity += parseInt($(this).val());
              });

              return totalQuantity;
            }

            const updateTotalQuantity = () => {
              let totalQuantity = getTotalQuantity();
              $('.devvn_sidebar_ft .devvn_cart_total_qty').html(totalQuantity);
            }

            const updateTotalPrice = amount_total => {
              $('.devvn_cart_fulltotal_price').html(amount_total)
            }

            const isExistIconQuantityHeader = () => $('.my_cart_quantity_header').length

            const updateIconQuantityHeader = quantity => {
                if(isExistIconQuantityHeader()) {
                    return $('.my_cart_quantity_header').html(quantity);
                }

                addIconQuantityHeader(quantity);
            }

            const addIconQuantityHeader = quantity => $('.cart-btn span').prepend(`
                <span class="uk-badge my_cart_quantity_header">
                    ${quantity}
                </span>
            `)

            const setEventRemoveItem = () => {
              $('.js_delete_product').unbind('click').click(function(event) {
                event.preventDefault();
                $(this).closest('.devvn_sidebar_entry').find('.js_quantity').val(0).trigger('change');
              })
            }

            /* CART DESKTOP */


            /* CART MOBILE */

            const updateNavCartMobile = response => {
              updateTotalQuantityMobile();

              updateTotalPriceMobile(response.amount_total);
            }

            const updateTotalQuantityMobile = () => {
              const totalQuantity = getTotalQuantity();

              if($('.quantity_monile').length) {
                return $('.quantity_monile').html(totalQuantity)
              }

              $('.dev_order_mobile .quantity').prepend(`
                <span class="quantity_monile" style="background: red; padding: 4px;">
                  ${totalQuantity}
                </span>
              `)
            };

            const updateTotalPriceMobile = amount_total => $('.dev-navbar-container .my_cart_quantity_total').html(amount_total)

            /* CART MOBILE */
            $('.popup_detail').unbind('click').click(function() {
                const id_product = $(this).closest('.box-items ').find('.product_id').val();
                
                const image = $(this).closest('.devvn_prd_list_option').find('img').attr('src');
                
                $('.devvn_popup_footer .css_quantity .quantity').val(1);

                ajax.jsonRpc("/shop/productCustomTest/"+id_product, 'call', {}).then(function (data){
                    data = JSON.parse(data);
                    setTimeout(function(){ 

                      setNamePopup(data, image);

                      renderOptions(data);

                      setEventSubmit();

                    },  10);
                })
            })
        });
    });