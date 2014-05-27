

/**
 *
 * Since the whole point of this app is that the python process is exposed to the 
 * web, we obviously need to take measures to protect our server.  This is done 
 * in several ways:
 *
 *		- The python process is deployed by a seperate server application that is 
 *			completely independant of the webserver.  Thus crashing the python 
 * 			server process will not take down the webserver.
 *		- The python server can be placed on a completely different machine
 *			than the web server.
 *		- Python is run in a sandboxed version of PyPy. See the pypy docs on 
 *			sandboxing http://doc.pypy.org/en/latest/sandbox.html
 *			- because of this, Python (or PyPy) has no direct file system access
 *			- 
 */


/**
 *
 * The Python RPC server provides a self-contained layer of abstraction over an
 * interactive python process. 
 *
 * the server listens on PORT for incoming 
 *
 */



// 'PORT' is the default port
// if no "--python_port=XXXX" parameter is provided to npm at start, the server will default to using 'PORT'
var PORT = 8085,

	// express app and socket.io to manage the websocket connection
	express = require('express'),
	app = express(),
	http = require('http'),
	server = http.createServer( app )
	io = require('socket.io').listen( server, { log : false } ),
	PythonInteract = require( __dirname + '/python-interact' ),
	python = new PythonInteract();



io.sockets.on( 'connection', function ( socket ) {

	socket.on( 'message', function ( msg, callback ) {
		
		// on incoming messages, determine whether python code is being sent from the web-server
		// TODO authentication stuffs should go here

		if ( msg.lang == 'python' && msg.data ) {

			python.exec( msg.data, function ( stdout ) {

				console.log(stdout)

				// response with the callback function
				callback( stdout );

			}, function ( stderr ) {

				// we're not currently doing anything with stderr
				// TODO

			});
		}

	});

});


/**
 * 
 * finally, start the server
 * if no "--port=XXXX" parameter is provided to npm at start, the server will default to using 'PORT'
 *
 */

server.listen( process.env.npm_config_python_port || PORT );

console.log( ">>> Python RPC Server running on port " + ( process.env.npm_config_python_port || PORT ) );


