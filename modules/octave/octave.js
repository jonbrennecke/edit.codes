
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