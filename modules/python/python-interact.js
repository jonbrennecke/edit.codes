
/**
 *
 * exports a manager for sandboxed interaction with python
 *
 */

var through = require('through'),
	spawn = require('child_process').spawn;

/**
 * 
 * Wrapper around the interactive Python pipe
 *
 * Start a python process and pipes it's stdout/stderr to handler methods
 *
 */
function PythonInteract () {

	// create readable and writeable stream
	this.__stdout = through();
	this.__stderr = through();

	this.start();

};	

PythonInteract.prototype = {

	// warn that the python process has closed
	close : function ( code, other ) { 

		console.warn(">>> Python closed with error-code " + code, other )

		// console.log(">>> Attempting to restart service");

		// this.start();

		// TODO, count number of tries to restart service
		// if number of retries exceeds 'n'. Give up with fail message.
	},


	// execute python code by passing it to the python stdin pipe
	// the stderr and stdout callbacks are called asynchronously
	// with the output from their repsective pipes
	exec : function ( input, stdoutCallback, stderrCallback ) {

		// output stdout
		this.__stdout.on( 'data', function ( data ) {

			stdoutCallback( data.toString() );

		});

		// output stderr
		this.__stderr.on( 'data', function ( data ) {

			stdoutCallback( data.toString() );

		});

		this.__python.stdin.write( input + '\n' );

	},

	// start or restart the service
	start : function () {

		// set $PYTHONPATH to include the pypy installation folder
		// and check if $PYTHONPATH is undefined so we don't concat "undefined" with the added path
		process.env["PYTHONPATH"] = ( typeof process.env["PYTHONPATH"] == "undefined" ? "" : process.env["PYTHONPATH"] ) + "/opt/pypy-sandbox/";
		
		this.__python = spawn( "python", [ "-u", "-i", "/usr/local/bin/pypy_interact.py", "/opt/pypy-sandbox/pypy/goal/pypy-c -u -i" ]);

		// pipe stdout/stderr to the writeable stream
		this.__python.stdout.pipe( this.__stdout );
		this.__python.stderr.pipe( this.__stderr );

		this.__python.on( 'close', this.close.bind( this ) );
	}

};


module.exports = PythonInteract;
