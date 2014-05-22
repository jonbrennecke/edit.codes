
// since the python process is exposed to the web we need to take
// measures to secure it. Thus:
// 		- the python process is seperate from the node server process
// 		- the python process is 

var through = require('through'),
	spawn = require('child_process').spawn;

// set up python
// ============================================================================================

// start python process
// parameters = [
// 		-i 	interactive prompt
// ]
var python = spawn( "python", [ "-i" ]);

// create readable and writeable stream using 'through'
var stdout = through();
var stderr = through();

// close the stream on exit
// python.on( 'exit', function () { 
// 	// writeStream.end();
// 	// readStream.end();
// });

// // pipe stdout/stderr to the writeable stream
python.stdout.pipe( stdout );
python.stderr.pipe( stderr );


module.exports = {
	process : python,
	stdout : stdout,
	stderr : stderr
}