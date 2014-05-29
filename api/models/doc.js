var mongoose = require('mongoose'),
	Schema = mongoose.Schema;

var DocSchema = new Schema({
	text : String,
	lang : String,
	ext : String
});

module.exports = mongoose.model( 'Doc', DocSchema);