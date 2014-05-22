/**
*
* UI/UX functions
*
*/

// toggle dropdown on the credits
$("#title-tab").click( function () {
	$('.layout').toggleClass('dropdown', { duration : 250, easing : "easeOutQuad" })
});

// toggle active on the editor tabs
$("#code-mirror-tabs li").click( function ( e ) {

	$( this.parentNode ).find("li").removeClass("active")
	$(this).addClass("active");

});

