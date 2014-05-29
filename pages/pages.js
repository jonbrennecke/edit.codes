/**
 *
 * Currates all the pages
 *
 */

var ide = require( __dirname + "/ide" ),
	users = require( __dirname + "/users" );
	

module.exports = {

	use : function ( app, passport ) {
		users.use( app, passport );
		ide.use( app, passport );
	}

}