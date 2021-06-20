/*
	TXT by HTML5 UP
	html5up.net | @ajlkn
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
*/

(function($) {

	$(".home-nav-a").click(function() {
		$([document.documentElement, document.body]).animate({
			scrollTop: 0
		}, 500);
	});

	$(".promotional-nav-a").click(function() {
		$([document.documentElement, document.body]).animate({
			scrollTop: $("#promotional-nav-location").offset().top - $("#nav").height()
		}, 500);
	});

	$(".features-nav-a").click(function() {
		$([document.documentElement, document.body]).animate({
			scrollTop: $("#features-nav-location").offset().top - $("#nav").height()
		}, 500);
	});

	$(".work-nav-a").click(function() {
		$([document.documentElement, document.body]).animate({
			scrollTop: $("#work-nav-location").offset().top - $("#nav").height()
		}, 500);
	});

	$(".documentation-nav-a").click(function() {
		$([document.documentElement, document.body]).animate({
			scrollTop: $("#documentation-nav-location").offset().top - $("#nav").height()
		}, 500);
	});

	$(".demos-nav-a").click(function() {
		$([document.documentElement, document.body]).animate({
			scrollTop: $("#demos-nav-location").offset().top - $("#nav").height()
		}, 500);
	});

	$(".team-nav-a").click(function() {
		$([document.documentElement, document.body]).animate({
			scrollTop: $("#team-nav-location").offset().top - $("#nav").height()
		}, 500);
	});

	$(".feature1-nav-a").click(function() {
		$([document.documentElement, document.body]).animate({
			scrollTop: $("#feature1-nav-location").offset().top - $("#nav").height() - 10
		}, 500);
	});
	$(".feature2-nav-a").click(function() {
		$([document.documentElement, document.body]).animate({
			scrollTop: $("#feature2-nav-location").offset().top - $("#nav").height() - 10
		}, 500);
	});
	$(".feature3-nav-a").click(function() {
		$([document.documentElement, document.body]).animate({
			scrollTop: $("#feature3-nav-location").offset().top - $("#nav").height() - 10
		}, 500);
	});
	$(".feature4-nav-a").click(function() {
		$([document.documentElement, document.body]).animate({
			scrollTop: $("#feature4-nav-location").offset().top - $("#nav").height() - 10
		}, 500);
	});
	$(".feature5-nav-a").click(function() {
		$([document.documentElement, document.body]).animate({
			scrollTop: $("#feature5-nav-location").offset().top - $("#nav").height() - 10
		}, 500);
	});
	$(".feature6-nav-a").click(function() {
		$([document.documentElement, document.body]).animate({
			scrollTop: $("#feature6-nav-location").offset().top - $("#nav").height() - 10
		}, 500);
	});
	$(".feature7-nav-a").click(function() {
		$([document.documentElement, document.body]).animate({
			scrollTop: $("#feature7-nav-location").offset().top - $("#nav").height() - 10
		}, 500);
	});

	$(document).scroll(function() {
		var y = $(this).scrollTop();
		$("#home-nav-li").removeClass("current");
		$("#features-nav-li").removeClass("current");
		$("#work-nav-li").removeClass("current");
		$("#team-nav-li").removeClass("current");
		$("#documentation-nav-li").removeClass("current");
		$("#demos-nav-li").removeClass("current");
		if (y >= $("#team-nav-location").offset().top - 1/3 * $(window).height()) {
			$("#team-nav-li").addClass("current");
		} else if (y >= $("#demos-nav-location").offset().top - 1/3 * $(window).height()) {
			$("#demos-nav-li").addClass("current");
		} else if (y >= $("#documentation-nav-location").offset().top - 1/3 * $(window).height()) {
			$("#documentation-nav-li").addClass("current");
		} else if (y >= $("#work-nav-location").offset().top - 1/3 * $(window).height()) {
			$("#work-nav-li").addClass("current");
		} else if (y >= $("#features-nav-location").offset().top - 1/5 * $(window).height()) {
			$("#features-nav-li").addClass("current");
		} else {
			$("#home-nav-li").addClass("current");
		}
	});


	$(".img-feature").click(function() {
		if ($(this).find("img").length != 0) {
			var img = $(this).children().children();
			$("#modal-img").attr("src", img.attr("src"));
			$("#modal").css("display", "block");
		} else if ($(this).find("iframe").length != 0) {
			var iframe = $(this).children().children();
			$("#iframe-modal-img").attr("src", iframe.attr("src"));
			$("#iframe-modal").css("display", "block");
		}
	});

	$(".modal-close, .toggle").click(function() {
		$("#modal").css("display", "none");
		$("#modal-img").attr("src", "");
		$("#iframe-modal").css("display", "none");
		$("#iframe-modal-img").attr("src", "");
	});


	var	$window = $(window),
		$body = $('body'),
		$nav = $('#nav');

	// Breakpoints.
		breakpoints({
			xlarge:  [ '1281px',  '1680px' ],
			large:   [ '981px',   '1280px' ],
			medium:  [ '737px',   '980px'  ],
			small:   [ '361px',   '736px'  ],
			xsmall:  [ null,      '360px'  ]
		});

	// Play initial animations on page load.
		$window.on('load', function() {
			window.setTimeout(function() {
				$body.removeClass('is-preload');
			}, 100);
		});

	// Dropdowns.
		$('#nav > ul').dropotron({
			mode: 'fade',
			noOpenerFade: true,
			speed: 300,
			alignment: 'center'
		});

	// Scrolly
		$('.scrolly').scrolly({
			speed: 1000,
			offset: function() { return $nav.height() - 5; }
		});

	// Nav.

		/* // Title Bar.
			$(
				'<div id="titleBar">' +
					'<a href="#navPanel" class="toggle"></a>' +
					'<span class="title">' + $('#logo').html() + '</span>' +
				'</div>'
			)
				.appendTo($body);

		// Panel.
			$(
				'<div id="navPanel">' +
					'<nav>' +
						$('#nav').navList() +
					'</nav>' +
				'</div>'
			)
				.appendTo($body)
				.panel({
					delay: 500,
					hideOnClick: true,
					hideOnSwipe: true,
					resetScroll: true,
					resetForms: true,
					side: 'left',
					target: $body,
					visibleClass: 'navPanel-visible'
				}); */

			$("#navPanel").panel({
				delay: 500,
				hideOnClick: true,
				hideOnSwipe: true,
				resetScroll: true,
				resetForms: true,
				side: 'left',
				target: $body,
				visibleClass: 'navPanel-visible'
			});

})(jQuery);