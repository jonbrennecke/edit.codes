
// get the Websocket client object from 'rpc-client.js'
var WSClient = require( __dirname + '/wsclient' );

// create an instance running on the port PORT
var wsclient = new WSClient( 'localhost', 8085 );

module.exports = function ( pythonData, callback ) {
		
	wsclient.send({
		lang : "python",
		data : pythonData
	}, callback );

};