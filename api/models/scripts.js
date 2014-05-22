var mongoose = require('mongoose'),
	Schema = mongoose.Schema;

var ScriptSchema = new Schema({
	stdin : String,
	lang : String,
	stdout : String,
	stderr : String
});

module.exports = mongoose.model('Script', ScriptSchema);