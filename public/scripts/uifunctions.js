/**
*
* UI/UX functions
*
*/

// toggle dropdown on the credits
$("#title-tab").click( function () {
	$('.layout').toggleClass('dropdown', { duration : 250, easing : "easeOutQuad" });
});


// toggle active on the editor tabs
$("#code-mirror-tabs li").click( function ( e ) {

	$( this.parentNode ).find("li").removeClass("active");
	$(this).addClass("active");

});


$("#profile-img-wrap .profile-img")

	// toggle visibility of the sign in/out menu
	.click( function () {
		$(this).toggleClass('dropped', { duration: 100, easing: "easeOutQuad" });
		$("#profile-drop-down").toggle({ duration: 200, easing: "easeOutQuad" });
	})

	// toggle gear icon
	.hover( function () {
		$(this).toggleClass('hover');
	});

