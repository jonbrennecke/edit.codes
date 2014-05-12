


$(document).ready( function () {

	// start CodeMirror
	// TODO pull this from a config json file
	// TODO dynamically get mode using require.js
	var codemirror = CodeMirror( document.getElementById('code-edit'), {
		value : "",
		mode : "octave",
		lineNumbers : true,
		theme : "monokai",
		indentUnit : 4,
		indentWithTabs : true,
		keymap : "sublime",
		autofocus : true,
		matchBrackets : true,
		autoCloseBrackets : true,
		highlightSelectionMatches : true
	});


	$( "#run" ).click( function ( e ) {

		// POST the data to the /run api endpoint
		$.ajax({	
			type : "post",
			url : "http://localhost:3000/api/run",
			data : { doc : codemirror.doc.getValue() },
			dataType : "json",
			complete : function ( response ) {

				var output = $("#code-output").empty();

				var stdout = response.responseJSON.stream.split('\n');

				for (var i = 0; i < stdout.length; i++) {
					output.append("<p>" + stdout[i] + "</p>")
				};
				
			}
		})
	});

});