/**
*
* WebSocket Client
*
*
*/

function WSClient( host, port ) {

	this.host = host;
	this.port = port;

	this.socket = require('socket.io-client').connect( 'http://' + host + ':' + port );

	// connect events with handlers
	this.socket.on( 'connect', this.onconnect.bind( this ) );
	this.socket.on( 'message', this.onmessage.bind( this ) );
	this.socket.on( 'error', this.onerror.bind( this ) );
	this.socket.on( 'close', this.onclose.bind( this ) );

};


WSClient.prototype = {

	// called immediately on connect
	onconnect : function () {
		console.log( ">>> Python RPC Client running on port " +  this.port );
	},

	// send a JSON object 'data' to the server
	// and do 'callback' asynchronously on response
	send : function ( data, callback ) {
		this.socket.emit( 'message', data, callback );
	},

	// handle responses from the server
	// TODO
	onmessage : function ( data ) {
		console.log( data )
	},

	onerror : function ( err ) {
		console.log( err )
	},

	onclose : function ( data ) {
		console.log( data )
	}
};

module.exports = WSClient;