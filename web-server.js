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
 * $ npm --mongodb_username=username --mongodb_password=password start
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
	bodyParser = require('body-parser'),
	router = express.Router(),
	app = express(),

	// filesystem libs
	sys = require('sys'),
	fs = require('fs'),
	childProcess = require('child_process'),
	exec = childProcess.exec,
	spawn = childProcess.spawn,

	// passport for authentication
	passport = require('passport'),
	LocalStrategy = require('passport-local').Strategy,

	// crypto for md5 hashing
	crypto = require('crypto'),
	
	// API Schemas
	Script = require( __dirname + '/api/models/scripts'),
	User = require( __dirname + '/api/models/user'),

	// language core modules
	python = require( __dirname + '/modules/python/python' ),

	// init the mongodb database
	db = require( __dirname + "/db.js" );


// Express app stuffs
// this part is kinda ugly and needs some cleaning up (TODO)
// ============================================================================================


// configure express
app.set('views', __dirname + '/public/jade/' );
app.set('view engine', 'jade');
app.engine( 'jade', require('jade').__express );
app.use( bodyParser() );

// TODO replace serving static files with NginX
app.use( express.static( __dirname + '/public/') );

app.use( passport.initialize() );
app.use( passport.session() );
app.use( '/api', router );


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



// render & serve 'public/haml/signup.haml' as the root file for now
// we'll be changing this later (TODO)
app.get('/', function ( req, res ){

	res.render("index", data );

});

// render & serve 'public/haml/signup.haml' as the root file for now
// we'll be changing this later (TODO)
app.get('/ide', function ( req, res ){

	res.render("ide", data );

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

// gets the IDE page
app.get('/ide', function ( req, res ){

	// render the jade and return the html
	res.render( 'ide' );

});


// gets the login page
app.get('/login', function ( req, res ){

	// render the jade and return the html
	res.render( 'login' );

});



// POST to login
app.post( '/login',
	
	passport.authenticate('local'),

	function(req, res) { {

		// If this function gets called, authentication was successful.
		// `req.user` contains the authenticated user.
		res.redirect('/users/' + req.user.name);
	
	}
});



// authenticate new user using passport
app.post('/register', function ( req, res ) {

	// attach POST to user schema
	var user = new User({ 

		email: req.body.email, 
		password: req.body.password, 
		name: req.body.username 

	});
	
	// save in Mongo
	user.save( function ( err ) {
		if( err ) {
			console.warn(err);
		} else {

			req.login( user, function(err) {
				if (err) {
					console.log(err);
				}
				return res.redirect('/');
			});

		}
	});

});


// 404 page
// app.use(function(req, res, next){
//   res.status(404);

//   // respond with html page
//   if (req.accepts('html')) {
//     res.render('404', { url: req.url });
//     return;
//   }

//   // respond with json
//   if (req.accepts('json')) {
//     res.send({ error: 'Not found' });
//     return;
//   }

//   // default to plain-text. send()
//   res.type('txt').send('Not found');
// });




// api endpoints
// ============================================================================================
// 

// Scripts API
// ============================================================================================
// POST api/scripts
// GET api/scripts
//

// router.route('/scripts')

// 	// add a script (accessed at POST http://localhost:3000/api/scripts)
// 	.post( function(req, res) {
		
// 		var script = new Script(); 	// create a new instance of the Script model
// 		script.name = req.body.name;  // set the Script name (comes from the request)

// 		// save the script and check for errors
// 		script.save( function(err) {
// 			if (err)
// 				res.send(err);

// 			res.json({ message: 'Script created!' });
// 		});
		
// 	})

// 	.get( function(req,res){
// 		Script.find(function(err, scripts) {
// 			if (err)
// 				res.send(err);

// 			res.json(scripts);
// 		});
// 	})


// Scripts API
// ============================================================================================
// POST api/run
//


router.route('/run')

	.post( function( req, res ) {
		
		var script = new Script();
		script.stdin = req.body.doc;
		
		
		python( script.stdin, function ( data ) {

			console.log( data )

		});


		// python.stdout.on( 'data', function ( data ) {

		// 	script.stdout = data.toString();
		// 	res.send( { "script" : script });

		// });

		// // python.stderr.on( 'data', function ( data ) {

		// // 	script.stderr = data.toString();
		// // 	res.send( { "script" : script });

		// // });


		// // probably should return the whole script model
		// python.process.stdin.write( script.stdin + '\n' );

		
	})



/**
 * 
 * finally, start the server
 * if no "--port=XXXX" parameter is provided to npm at start, the server will default to using 'PORT'
 *
 */
app.listen( process.env.npm_config_port || PORT );

console.log(">>> magic happening on port " + ( process.env.npm_config_port || PORT ) );



