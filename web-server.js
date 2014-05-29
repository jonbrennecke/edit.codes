/**
 *                            
 * d88888b d8888b. d888888b d888888b     .o88b.  .d88b.  d8888b. d88888b .d8888. 
 * 88'     88  `8D   `88'   `~~88~~'    d8P  Y8 .8P  Y8. 88  `8D 88'     88'  YP 
 * 88ooooo 88   88    88       88       8P      88    88 88   88 88ooooo `8bo.   
 * 88~~~~~ 88   88    88       88       8b      88    88 88   88 88~~~~~   `Y8b. 
 * 88.     88  .8D   .88.      88    db Y8b  d8 `8b  d8' 88  .8D 88.     db   8D 
 * Y88888P Y8888D' Y888888P    YP    VP  `Y88P'  `Y88P'  Y8888D' Y88888P `8888Y' 
 *
 *
 *
 * This project is hosted as a GitHub repository at github.com/jonbrennecke/edit.codes
 * 
 *
 * ~~~~~~~~~~~~~~~~~~~~~~~~ USAGE ~~~~~~~~~~~~~~~~~~~~~~~~
 *
 * This script should be run with username/password parameters for the MongoLab database
 * supplied as command-line arguments, i.e. :
 *
 * $ npm --mongodb_username=username --mongodb_password=password --secret=secret start
 * 
 * An additional 'port' parameter can be provided, instructing the server on which port to 
 * listen. The port should be provided like "--port=8080"
 *
 *
 */


/**
 * first check the command line arguments for the MongoLab username/password
 * these should be passed to npm as:
 *
 * npm --mongodb_username=username --mongodb_password=password start
 */

if ( ! ( process.env.npm_config_mongodb_username && process.env.npm_config_mongodb_password ) ) {
	console.error( 
		"ERROR >>> requires MongoDB "  + 
		( process.env.npm_config_mongodb_username ? ( process.env.npm_config_mongodb_password ? 
		"" : "password" ) : "username and password" ) + " as CLI argument(s)" 
	);

	process.exit();
}


// first let's define some constants and requires
// ============================================================================================

// 'PORT' is the default port
// if no "--port=XXXX" parameter is provided to npm at start, the server will default to using 'PORT'

var PORT = 3000,

	// get expressjs and a few other things
	express = require('express'),
	session = require('express-session'),
	cookieParser = require('cookie-parser'),
	bodyParser = require('body-parser'),
	router = express.Router(),
	app = express(),

	// passport for authentication
	passport = require('passport'),
	LocalStrategy = require('passport-local').Strategy,

	// to make passport work with MongoDb
	MongoStore = require('connect-mongo')(session),
	
	// API Schemas
	Script = require( __dirname + '/api/models/scripts'),
	User = require( __dirname + '/api/models/user'),

	// language core modules
	python = require( __dirname + '/modules/python/python' ),

	// init the mongodb database
	db = require( __dirname + "/db.js" );



/**
 *
 *  Configure Express
 *
 */

app.set('views', __dirname + '/public/jade/' );
app.set('view engine', 'jade');
app.engine( 'jade', require('jade').__express );
app.use( bodyParser() );
app.use( cookieParser() );

// TODO replace serving static files with NginX
app.use( express.static( __dirname + '/public/') );

app.use( passport.initialize() );
app.use( session({
	secret : process.env.npm_config_secret,
	cookie : {
		maxAge : 3600000
	},
	store : new MongoStore({
		mongoose_connection : db
	})
}));
app.use( passport.session() );
app.use( '/api', router );


/**
 *
 * passport requires these functions to serialize user info for a persistant session
 *
 */

passport.serializeUser( function(user, done) {
	done(null, user.id);
});

passport.deserializeUser( function(id, done) {
	User.findById(id, function (err, user) {
		done(err, user);
	});
});


// set up passport for local authentication
passport.use( new LocalStrategy(
	function ( username, password, done ) {

		User.findOne({ name: username }, function(err, user) {
			
			if ( err ) { return done( err ); }
			
			if ( ! user ) {
				return done(null, false, { message: 'Incorrect username.' });
			} 

			if ( ! user.checkPassword( password ) ) {
				return done(null, false, { message: 'Incorrect password.' });
			}

			return done(null, user);
		});
	}
));


/**
 *
 * The API/Pages schemas are seperated into several files
 * require and run these
 *
 */

// api
var api = require( __dirname + '/api/api' );
api.use( app, router );


// pages
var pages = require( __dirname + '/pages/pages' );
pages.use( app, passport );



/**
 * 
 * finally, start the server
 * if no "--port=XXXX" parameter is provided to npm at start, the server will default to using 'PORT'
 *
 */


app.listen( process.env.npm_config_port || PORT );

console.log(">>> magic happening on port " + ( process.env.npm_config_port || PORT ) );



