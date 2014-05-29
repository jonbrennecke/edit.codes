/**
 *
 * handles routing for user login/signup
 *
 * Endpoints:
 *	- /login - 
 *	- /signup - 
 * 	- /signout - ends session and redirects to home page
 */

module.exports = {
	
	use : function ( app, passport ) {

		app
			.post( '/login', passport.authenticate('local', {
				successRedirect : "/",
				failureRedirect : "/login"
			}))
			.get( '/login', function ( req, res ) {

				if ( req.user ) res.redirect('/')
				else res.render("login");

			});

	}

};