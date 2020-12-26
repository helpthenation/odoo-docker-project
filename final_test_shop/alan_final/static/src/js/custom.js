/*
 * jQuery.appear
 * https://github.com/bas2k/jquery.appear/
 * http://code.google.com/p/jquery-appear/
 * http://bas2k.ru/
 *
 * Copyright (c) 2009 Michael Hixson
 * Copyright (c) 2012-2014 Alexander Brovikov
 * Licensed under the MIT license (http://www.opensource.org/licenses/mit-license.php)
 */
(function($) {
    $.fn.appear = function(fn, options) {

        var settings = $.extend({

            //arbitrary data to pass to fn
            data: undefined,

            //call fn only on the first appear?
            one: true,

            // X & Y accuracy
            accX: 0,
            accY: 0

        }, options);

        return this.each(function() {

            var t = $(this);

            //whether the element is currently visible
            t.appeared = false;

            if (!fn) {

                //trigger the custom event
                t.trigger('appear', settings.data);
                return;
            }

            var w = $(window);

            //fires the appear event when appropriate
            var check = function() {

                //is the element hidden?
                if (!t.is(':visible')) {

                    //it became hidden
                    t.appeared = false;
                    return;
                }

                //is the element inside the visible window?
                var a = w.scrollLeft();
                var b = w.scrollTop();
                var o = t.offset();
                var x = o.left;
                var y = o.top;

                var ax = settings.accX;
                var ay = settings.accY;
                var th = t.height();
                var wh = w.height();
                var tw = t.width();
                var ww = w.width();

                if (y + th + ay >= b &&
                    y <= b + wh + ay &&
                    x + tw + ax >= a &&
                    x <= a + ww + ax) {

                    //trigger the custom event
                    if (!t.appeared) t.trigger('appear', settings.data);

                } else {

                    //it scrolled out of view
                    t.appeared = false;
                }
            };

            //create a modified fn with some additional logic
            var modifiedFn = function() {

                //mark the element as visible
                t.appeared = true;

                //is this supposed to happen only once?
                if (settings.one) {

                    //remove the check
                    w.unbind('scroll', check);
                    var i = $.inArray(check, $.fn.appear.checks);
                    if (i >= 0) $.fn.appear.checks.splice(i, 1);
                }

                //trigger the original fn
                fn.apply(this, arguments);
            };

            //bind the modified fn to the element
            if (settings.one) t.one('appear', settings.data, modifiedFn);
            else t.bind('appear', settings.data, modifiedFn);

            //check whenever the window scrolls
            w.scroll(check);

            //check whenever the dom changes
            $.fn.appear.checks.push(check);

            //check now
            (check)();
        });
    };

    //keep a queue of appearance checks
    $.extend($.fn.appear, {

        checks: [],
        timeout: null,

        //process the queue
        checkAll: function() {
            var length = $.fn.appear.checks.length;
            if (length > 0) while (length--) ($.fn.appear.checks[length])();
        },

        //check the queue asynchronously
        run: function() {
            if ($.fn.appear.timeout) clearTimeout($.fn.appear.timeout);
            $.fn.appear.timeout = setTimeout($.fn.appear.checkAll, 20);
        }
    });

    //run checks when these methods are called
    $.each(['append', 'prepend', 'after', 'before', 'attr',
        'removeAttr', 'addClass', 'removeClass', 'toggleClass',
        'remove', 'css', 'show', 'hide'], function(i, n) {
        var old = $.fn[n];
        if (old) {
            $.fn[n] = function() {
                var r = old.apply(this, arguments);
                $.fn.appear.run();
                return r;
            }
        }
    });

})(jQuery);
/* Progress End*/





$(window).scroll(function() {
    if ($(window).scrollTop() >= 50) {
        $('body').addClass('fixed-header');
    } else {
        $('body').removeClass('fixed-header');
    }
});

$(document).ready(function() {

    $("#as-pro-slide").owlCarousel({
        items: 4,
        margin: 30,
        navigation: true,
        pagination: false,
        responsive: {
            0: {
                items: 1,
            },
            481: {
                items: 2,
            },
            768: {
                items: 3,
            },
            1024: {
                items: 4,
            }
        }

    });

    $("#as-featured-slide").owlCarousel({
        items: 4,
        margin: 30,
        navigation: true,
        pagination: false,
        responsive: {
            0: {
                items: 1,
            },
            481: {
                items: 2,
            },
            768: {
                items: 3,
            },
            1024: {
                items: 4,
            }
        }

    });

    $("#as_our_brand").owlCarousel({
        items: 6,
        margin: 10,
        navigation: true,
        pagination: false,
        responsive: {
            0: {
                items: 2,
            },
            481: {
                items: 2,
            },
            768: {
                items: 4,
            },
            1024: {
                items: 8,
            }
        }

    });

    $("#pro_detail_zoom").owlCarousel({
        items:4,
        margin: 10,
        navigation: true,
        pagination: false
    });


    /*$(".view-mode .shift_list_view").click(function(e) {
        e.preventDefault();
        $('#products_grid').addClass("list-view-box");
        
    });
    $(".view-mode .shift_grid_view").click(function(e) {
        e.preventDefault();
        $('#products_grid').removeClass("list-view-box");
    });*/

    /* list grid view 
    ===================*/
    $(".oe_website_sale .shift_list_view").click(function(e) {
        $(".oe_website_sale .shift_grid_view").removeClass('active')
        $(this).addClass('active')
        $('#products_grid').addClass("list-view-box");
        localStorage.setItem("product_view", "list");
    });
    $(".oe_website_sale .shift_grid_view").click(function(e) {
        $(".oe_website_sale .shift_list_view").removeClass('active')
        $(this).addClass('active')
        $('#products_grid').removeClass("list-view-box");
        localStorage.setItem("product_view", "grid");
    });
    if (localStorage.getItem("product_view") == 'list') {
        $(".oe_website_sale .shift_grid_view").removeClass('active')
        $(".oe_website_sale .shift_list_view").addClass('active')
        $('#products_grid').addClass("list-view-box");
    }
    if (localStorage.getItem("product_view") == 'grid') {
        $(".oe_website_sale .shift_list_view").removeClass('active')
        $(".oe_website_sale .shift_grid_view").addClass('active')
        $('#products_grid').removeClass("list-view-box");
    }


    /*full widht banner*/
    function setHeight() {
        windowHeight = $(window).innerHeight() - $('header').outerHeight();
        $('.as-animated-slider .slide').css('min-height', windowHeight);
      };
      setHeight();
      
      $(window).resize(function() {
        setHeight();
      });

      /**/

      /* Progress
      /-----------------------------------------------*/
	  
       if ($("[data-animate-width]").length>0) {
            $("[data-animate-width]").each(function() {
                $(this).appear(function() {
                    $(this).animate({
                        width: $(this).attr("data-animate-width")
                    }, 800 );
                }, {accX: 0, accY: -100});
            });
        };

        
      

        // Gallery 
        //-----------------------------
        if ($(".slider-popup-img") && $(".slider-popup-img").length > 0) {
           $(".slider-popup-img").magnificPopup({
               type:"image",
               gallery: {
                   enabled: true,
               }
           });
       }
		$('img.theme-slider-gallary').on('load', function (ev) {
			var $link = $(ev.currentTarget);
			var a=$link.parent().find("a");
			a.attr('href',this.src);		
		});
        if ($(".slider-popup-product") && $(".slider-popup-product").length > 0) {
           $(".slider-popup-product").magnificPopup({
               type:"image",
               gallery: {
                   enabled: true,
               }
           });
       }

});


jQuery(document).ready(function($) {
    // browser window scroll (in pixels) after which the "back to top" link is shown
    var offset = 300,
        //browser window scroll (in pixels) after which the "back to top" link opacity is reduced
        offset_opacity = 1200,
        //duration of the top scrolling animation (in ms)
        scroll_top_duration = 700,
        //grab the "back to top" link
        $back_to_top = $('.cd-top');

    //hide or show the "back to top" link
    $(window).scroll(function() {
        ($(this).scrollTop() > offset) ? $back_to_top.addClass('cd-is-visible'): $back_to_top.removeClass('cd-is-visible cd-fade-out');
        if ($(this).scrollTop() > offset_opacity) {
            $back_to_top.addClass('cd-fade-out');
        }
    });

    //smooth scroll to top
    $back_to_top.on('click', function(event) {
        event.preventDefault();
        $('body,html').animate({
            scrollTop: 0,
        }, scroll_top_duration);
    });


    //Mobile menu
    $(".mm-mega-menu > a").click(function() {
        $(this).parent().toggleClass("open-mob-menu");
        $(this).toggleClass("mob-menu-open");
    });

    /*$(".hm-search .hm-search-hide").click(function() {
        $('body').toggleClass("hm-search-open");
    });*/
    
    /* $(function() {
        $('.hm-search .hm-search-hide').on('click',
        function(event) {
            event.stopPropagation();
            $('.hm-search-box').toggleClass('hm-search-open');
        });
        $('html').click(function() {
            $('.hm-search-box').removeClass('hm-search-open');
        });
    });*/

     /*$(function() {
      $(".hm-search .hm-search-hide").on("click", function(e) {
        $(".hm-search-box").addClass("hm-search-open");
        e.stopPropagation()
      });
      $(document).on("click", function(e) {
        if ($(e.target).is(".hm-search-box") === false) {
          $(".hm-search-box").removeClass("hm-search-open");
        }
      });
    });*/

     $(".hm-search .hm-search-hide").on("click", function(event){
        $(".hm-search-box").toggleClass("hm-search-open");
        event.stopPropagation();
    });
    $(".hm-search-box").on("click", function(event){
        event.stopPropagation();
    });
    $(document).on("click", function(event){
        $(".hm-search-box").removeClass("hm-search-open");
    });


    // zoom slider

$('.main_image .img').elevateZoom({
        constrainType:"height", 
        constrainSize:274, 
        zoomType: "lens",
        lensShape: "square",
        containLensZoom: true, 
        gallery:'gallery_01', 
        cursor: 'pointer', 
        galleryActiveClass: "active"
    });
$('.js_variant_img').elevateZoom({
        constrainType:"height", 
        constrainSize:274, 
        zoomType: "lens",
        lensShape: "square",
        containLensZoom: true, 
        gallery:'gallery_01', 
        cursor: 'pointer', 
        galleryActiveClass: "active"
    });

    $('.counter-portfolio').counterUp({
        delay: 20,
        time: 1000
    });
    $('.counter-blog-template').counterUp({
        delay: 20,
        time: 1000
    });
    $('.counter-shortcut').counterUp({
        delay: 20,
        time: 1000
    });
    $('.counter-like').counterUp({
        delay: 20,
        time: 1000
    });



});

 
 

