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
 * $ node server.js user pass
 * 
 *
 *
 */



// first check the command line arguments for the MongoLab username/password
// ============================================================================================

if ( ! ( process.argv[2] && process.argv[3] ) ) {
	
	console.error( "ERROR >>> requires MongoDB "  + 
		( process.argv[2] ? ( process.argv[3] ? "" : "password" ) : "username and password" ) +
		" as CLI argument(s)" );

	process.exit();

}



// first let's define some constants and requires
// ============================================================================================

// define what port the server will run on
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
	
	// API Schemas
	Script = require( __dirname + '/api/models/scripts'),
	User = require( __dirname + '/api/models/user'),

	// init the mongodb database
	db = require( __dirname + "/db.js" );




// Express app stuffs
// this part is kinda ugly and needs some cleaning up (TODO)
// ============================================================================================


// configure express
app.use( bodyParser() );
app.use( express.static( __dirname + '/public/') );
app.use( passport.initialize() );
app.use( passport.session() );
app.use( '/api', router );


/**
 *
 * passport requires these functions to serialize user info for a persistant session
 *
 */

passport.serializeUser(function(user, done) {
	done(null, user.id);
});

passport.deserializeUser(function(id, done) {
	User.findById(id, function (err, user) {
		done(err, user);
	});
});



// render & serve 'public/haml/signup.haml' as the root file for now
// we'll be changing this later (TODO)
app.get('/', function ( req, res ){

	// compile the HAML and return the HTML
	exec("haml public/haml/dash.haml", function ( error, html ) {
		if ( error ) {
			throw error;
		}

		res.send( html );
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



// gets the login page
app.get('/login', function ( req, res ){

	// compile the HAML and return the HTML
	exec("haml public/haml/login.haml", function ( error, html ) {
		if ( error ) {
			throw error;
		}

		res.send( html );
	});

});



// POST to login
app.post( '/login',
	
	passport.authenticate('local'),

	function(req, res) { {

		console.log('here')

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
// router.route('/run')

// 	.post( function( req, res ) {
		
// 		var script = new Script();
// 		script.doc = req.body.doc;

// 		// save the script and check for errors
// 		script.save( function(err) {
// 			if (err)
// 				res.send(err);

// 			octave.stdout.on( 'data', function ( data ) {

// 				fs.readFile('tmp.out', "utf8", function (err, data) {
// 			        if (err) throw err;
// 				        res.send( { "stream" : "" + data } )
// 			        });
// 			    // }
// 			});

// 			octave.stdin.write( script.doc + '\n' );

// 		});
		
// 	})



// finally, start the server
// ============================================================================================
app.listen( PORT );

console.log(">>> magic happening on port " + PORT );