// RequireJS asynchronously loads our modules 

requirejs.config({
	
	paths : {

		// jquery
		'jquery' : 'libs/jquery',
		'jquery-ui' : 'libs/jquery-ui.min'
	},

	shim : {

		'jquery' : {
			exports : '$'
		},
		
		'jquery-ui' : {
			exports : '$',
			deps : ['jquery']
		},

		'uifunctions' : {
			deps : [ 'jquery-ui' ]
		}
	}

});


// shortened names for CodeMirror paths
// these shoud be passed to requirejs.config as 'paths', but then CodeMirror's internal 
// requires break
var cm = {
	main : 'bower_components/CodeMirror/lib/codemirror',
	search : 'bower_components/CodeMirror/addon/search/search',
	searchcursor : 'bower_components/CodeMirror/addon/search/searchcursor',
	dialog : 'bower_components/CodeMirror/addon/dialog/dialog',
	matchbrackets : 'bower_components/CodeMirror/addon/edit/matchbrackets',
	closebrackets : 'bower_components/CodeMirror/addon/edit/closebrackets',
	comment : 'bower_components/CodeMirror/addon/comment/comment',
	hardwrap : 'bower_components/CodeMirror/addon/wrap/hardwrap', 
	foldcode : 'bower_components/CodeMirror/addon/fold/foldcode', 
	bracefold : 'bower_components/CodeMirror/addon/fold/brace-fold',
	sublime : 'bower_components/CodeMirror/keymap/sublime',
	python : 'bower_components/CodeMirror/mode/python/python'
};


// load jQuery and init the ui functions
define( [ "jquery-ui", "uifunctions" ], function ( $ ) {

	// the ide script initiates CodeMirror and sets up ajax requests to 
	// the server's api endpoint for script execution
	require(['ide']);

});