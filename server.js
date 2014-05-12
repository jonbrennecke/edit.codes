/*
 *
 *
 * Server
 *
 *
 */


// constants and requires
// ============================================================================================
var PORT = 3000,
	express = require('express'),
	bodyParser = require('body-parser'),
	sys = require('sys'),
	fs = require('fs'),
	childProcess = require('child_process'),
	exec = childProcess.exec,
	spawn = childProcess.spawn,
	passport = require('passport'),

	// express
	router = express.Router(),
	app = express(),
	
	// API Schemas
	Script = require('./api/scripts'),
	Command = require('./api/cmd'),

	// init the mongodb database
	db = require( __dirname + "/db.js" );




// set up octave
// ============================================================================================

// start octave process
// parameters = [
// 		-q 	"quiet", don't print welcome message
// 		-i 	interactive prompt
// 		-w   disable any windowing functions
// ]
var octave = spawn( "octave", [ "-q", "-i", "-W" ]);

// create readable and writeable streams to 'tmp.out'
var writeStream = fs.createWriteStream('tmp.out');
var readStream = fs.createReadStream('tmp.out');

// close the stream on exit
octave.on( 'exit', function () { 
	writeStream.end();
});

octave.stdout.pipe( writeStream );




// check command line arguments
// ============================================================================================

if ( ! ( process.argv[2] && process.argv[3] ) ) {
	
	console.error( "ERROR >>> requires MongoDB "  + 
		( process.argv[2] ? ( process.argv[3] ? "" : "password" ) : "username and password" ) +
		" as CLI argument(s)" );

	process.exit();

}



// Express app stuffs
// ============================================================================================



// allows us to get JSON data from a POST
app.use( bodyParser() );


// render & serve 'public/haml/index.haml' as the root file
app.get('/', function(req, res){

	// compile the HAML and return the HTML
	exec("haml public/haml/index.haml", function ( error, html ) {
		if ( error ) {
			throw error;
		}

		res.send( html );
	});

});


// serve the public folder as static content
app.use( express.static( __dirname + '/public/') );


// ============================================================================================
// app.post("/login", function () {

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
		script.doc = req.body.doc;

		// save the script and check for errors
		script.save( function(err) {
			if (err)
				res.send(err);

			octave.stdout.on( 'data', function ( data ) {

				fs.readFile('tmp.out', "utf8", function (err, data) {
			        if (err) throw err;
				        res.send( { "stream" : "" + data } )
			        });
			    // }
			});

			octave.stdin.write( script.doc + '\n' );

		});
		
	})

app.use('/api', router );


// function ( req, res ) {
// 	exec( req.body.cmd, config, puts )
// });

// serve static files from the /public/ folder
//app.use( express.static( __dirname + '/public/') );

// start the server
// ============================================================================================
app.listen(PORT);

console.log(">>> magic happening on port " + PORT );