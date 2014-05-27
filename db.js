/**
 * 
 * connect to MongoDB on MongoLab
 *
 */


var mongoose = require('mongoose'),
	mongoUrl = "dbh55.mongolab.com:27557/api";


// mongodb error handler
mongoose.connection.on("error", function ( err ) {
	
	if ( err.code == 18 ) { // authentication fail
		
		console.error( "ERROR >>> MongoDB authentication failed" );

		process.exit();

	}

	// otherwise demote the error to a warning
	else console.warn( err );

});


// once a connection is opened
mongoose.connection.on( "open", function ( res ) {

	console.log( ">>> opened mongodb connection at " + mongoUrl );

});


// try authenticating with the username and password given as arguments
mongoose.connect("mongodb://" + process.env.npm_config_mongodb_username + ":" + process.env.npm_config_mongodb_password + "@" + mongoUrl );