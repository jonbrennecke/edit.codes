( function ( mod ){

	require( [ 
		cm.main, 
		cm.search,
		cm.searchcursor,
		cm.dialog,
		cm.matchbrackets,
		cm.closebrackets,
		cm.comment,
		cm.hardwrap,
		cm.foldcode,
		cm.bracefold,
		cm.sublime,
		cm.python ], mod );;

})( function ( CodeMirror ) {

	$( document ).ready( function () {
					
		// start CodeMirror
		var codemirror = CodeMirror( document.getElementById( 'code-mirror' ), {


			value:  
					'# ┌─┐┬ ┬┌┬┐┬ ┬┌─┐┌┐┌\n'+
					'# ├─┘└┬┘ │ ├─┤│ ││││\n'+
					'# ┴   ┴  ┴ ┴ ┴└─┘┘└┘\n\n'+

					'def main () :\n' +
					'\tprint "hello world!"\n\n' + 

					'if __name__ == "__main__":\n' + 
					'\tmain()\n',

			indentUnit : 4,
			indentWithTabs : true,
		    lineNumbers: true,
		    mode: "python",
		    keyMap: "sublime",
		    autoCloseBrackets: true,
		    autofocus : true,
		    matchBrackets: true,
		    showCursorWhenSelecting: true,
		    theme: "monokai"
		});

	
		$( "#run" ).click( function ( e ) {

			// POST the data to the /run api endpoint
			$.ajax({	
				type : "post",
				url : "http://localhost:3001/api/run",
				data : { doc : codemirror.doc.getValue() },
				dataType : "json",
				complete : function ( response ) {

					console.log(response)

					var output = $("#console").empty();

					var stdout = response.responseJSON.script.stdout.split('\n');

					for (var i = 0; i < stdout.length; i++) {
						output.append("<p>" + stdout[i] + "</p>")
					};
					
				}
			});
		});
	});
});