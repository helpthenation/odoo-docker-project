
	$(document).ready(function() {

		if($('.devvn_fix_scroll').length > 0){
			var topMargin = 150;
			var $animation_elements = $('.devvn_fix_scroll');
			var $window = $(window);
			var element_top_position = $animation_elements.offset().top;
			function check_if_in_view() {
				var con_ofset_top	= $('.devvn_order_content').offset().top;
				var con_height		= $('.devvn_order_content').height();
				var con_fix_height	= con_ofset_top+con_height;
				var window_top_position = $window.scrollTop();

				$.each($('.devvn_fix_scroll'), function() {
					var el_height	= $(this).outerHeight();
					var el_width	= $(this).outerWidth();
					if ((window_top_position+topMargin >= element_top_position) ) {
						$(this).css({'width':el_width+'px','top':topMargin+'px'}).addClass('in_view');
					} else {
						$(this).removeAttr('style').removeClass('in_view');
					}
					if ((el_height+window_top_position >= con_fix_height) ) {
						$(this).addClass('in_view_bot');
					} else {
						$(this).removeClass('in_view_bot');
					}
				});
			}
			function scroll_in_view() {
				var window_height = $window.height();
				var window_top_position = $window.scrollTop();
				var window_bottom_position = (window_top_position + window_height);

				$.each($('.devvn_term_item'), function() {
					var $element = $(this);
					var data_scroll	= $(this).data('scroll');
					var element_height = $element.outerHeight();
					var element_top_position = $element.offset().top - 50;
					var element_bottom_position = (element_top_position + element_height);

					//check to see if this current container is within viewport
					if ((element_top_position <= window_top_position) || (window_top_position >= element_top_position )) {
						$('.devvn_cat_select').removeClass('active');
						$(data_scroll).addClass('active');
					}
				});
			}
			$window.on('scroll load resize', check_if_in_view);
			$window.on('scroll load resize', scroll_in_view);
		}
		//

	});
