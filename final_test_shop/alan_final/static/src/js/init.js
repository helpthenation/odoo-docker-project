
const convertToEnglish = (alias) => {
    var str = alias;
    str = str.toLowerCase();
    str = str.replace(/à|á|ạ|ả|ã|â|ầ|ấ|ậ|ẩ|ẫ|ă|ằ|ắ|ặ|ẳ|ẵ/g,"a"); 
    str = str.replace(/è|é|ẹ|ẻ|ẽ|ê|ề|ế|ệ|ể|ễ/g,"e"); 
    str = str.replace(/ì|í|ị|ỉ|ĩ/g,"i"); 
    str = str.replace(/ò|ó|ọ|ỏ|õ|ô|ồ|ố|ộ|ổ|ỗ|ơ|ờ|ớ|ợ|ở|ỡ/g,"o"); 
    str = str.replace(/ù|ú|ụ|ủ|ũ|ư|ừ|ứ|ự|ử|ữ/g,"u"); 
    str = str.replace(/ỳ|ý|ỵ|ỷ|ỹ/g,"y"); 
    str = str.replace(/đ/g,"d");
    str = str.replace(/!|@|%|\^|\*|\(|\)|\+|\=|\<|\>|\?|\/|,|\.|\:|\;|\'|\"|\&|\#|\[|\]|~|\$|_|`|-|{|}|\||\\/g," ");
    str = str.replace(/ + /g," ");
    str = str.trim(); 
    return str;
}

const renderCartEmpty = () => {
	$('.devvn_cart_coupon').hide(); 
	$('.devvn_checkout').hide();
	$('.remove_cart_shop').closest('div').hide();
	$('.cart_o_mobile').closest('div').show();
	setDefaultValue();
}

const setDefaultValue = () => {
	$('.devvn_sidebar_entry').remove();
	$('.devvn_cart_total_qty').html('');
	$('.my_cart_quantity_total').html(0);
}

const renderCartNotEmpty = () => {
	$('.devvn_cart_coupon').show(); 
	$('.devvn_checkout').show();
  $('.devvn_checkout').removeClass('hidden');
	$('.remove_cart_shop').closest('div').show();
	$('.cart_o_mobile').closest('div').hide();
}

const isEmptyCart = () => $('.devvn_sidebar_entry').length < 1;

const renderTemplateCart = () => {
	isEmptyCart() ? renderCartEmpty() : renderCartNotEmpty();
}



/* GOOGLE MAP */
let country = city = district = ward = '';

const getIdCountry = country => {
   let id_conutry =  $('#country_id option:eq(1)').val();

   $('#country_id option').each(function() {
      const text = $(this).text().trim().toLowerCase().split(' ').join('');
      country = convertToEnglish(country.trim().toLowerCase()).split(' ').join('');

      if(convertToEnglish(text).indexOf(country) !== -1) {
         id_conutry = $(this).val();
      }
   })

   return id_conutry;
}

const getIdCity = city => {
   let id_city =  $('#state_id option:eq(0)').val();

   $('#state_id option').each(function() {
      const text = $(this).text().trim().toLowerCase();
      city = convertToEnglish(city.trim().toLowerCase());

      if(convertToEnglish(text).indexOf(city) !== -1) {
         id_city = $(this).val();
      }
   })

   return id_city;
}

const getIdDistrict = district => {
   district = district.replace('District', '').toLowerCase().trim();
   let id_district =  $('#district_id option:eq(0)').val();

   $('#district_id option').each(function() {
      const text = $(this).text().trim().toLowerCase();
      district = convertToEnglish(district);
      if(convertToEnglish(text).indexOf(district) !== -1) {
         id_district = $(this).val();
      }
   })

   return id_district;
}

const getIdWard = ward => {
   let id_ward =  $('#ward_id option:eq(0)').val();

   $('#ward_id option').each(function() {
      const text = $(this).text().trim().toLowerCase();
      ward = convertToEnglish(ward.trim().toLowerCase());

      if(convertToEnglish(text).indexOf(ward) !== -1) {
         id_ward = $(this).val();
      }
   })

   return id_ward;
}

// const disabledButtonPayment = () => {
// 	$('.button_payment').attr('disabled', 'disabled');
// 	$('.button_payment a').removeClass('a-submit');
// 	$('.button_payment a').attr('href', 'javascript:void(0)');
// }
//
// const enableButtonPayment = () => {
// 	$('.button_payment').removeAttr('disabled');
// 	$('.button_payment a').addClass('a-submit');
// 	$('.button_payment a').attr('href', '/shop/confirm_order');
// }

// (function () {
// 	disabledButtonPayment();
// })();

const hiddenBlockItem = () => {
  $('.devvn_section_category').each(function() {
      const status = $(this).find('.box-items').length > 0;
      const title = $(this).find('.devvn_term_title').text().trim().toLowerCase();
      $(this).toggle(status);
      toggleCategory(title, status);
  })
}

const toggleCategory = (title, status) => {
  $('.devvn_menu_nav .devvn_cat_select').each(function() {
    const titleCategory = $(this).text().trim().toLowerCase();
    if(titleCategory === title) {
      $(this).closest('.devvn_cat_li').toggle(status);
    }
  })
}

$(document).ready(function () {
    hiddenBlockItem();
})

/* GOOGLE MAP */
