var mongoose = require('mongoose'),
	Schema = mongoose.Schema;

var ScriptSchema = new Schema({
	doc : String,
	lang : String,
});

module.exports = mongoose.model('Script', ScriptSchema);