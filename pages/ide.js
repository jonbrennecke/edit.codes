/**
 *
 * render and serve the IDE page
 *
 */

// crypto for md5 hashing
crypto = require('crypto');


// serialize the user data
// TODO put this in a module and load asyncly

// generate a link to the user's gravatar
var gravatar = "http://www.gravatar.com/avatar/";
gravatar += crypto.createHash('md5').update( "jpbrennecke@gmail.com".toLowerCase().trim() ).digest("hex");
gravatar += "?s=256";

var data = {
	user : {
		name : "Jon",
		email : "jpbrennecke@gmai.com",
		gravatar : gravatar
	}
}



module.exports = {
	
	use : function ( app, passport ) {

		app.get('/', function ( req, res ){

			console.log(req.user)

			res.render("ide", data );

		});

	}

}