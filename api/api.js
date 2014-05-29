var user = require( __dirname + "/user" );

module.exports = {
	
	use : function ( app, router ) {

		user.use( app, router );

	}

};