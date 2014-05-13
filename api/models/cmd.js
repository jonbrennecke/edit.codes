var mongoose = require('mongoose'),
	Schema = mongoose.Schema;

var CMDSchema = new Schema({
	input : String
});

module.exports = mongoose.model('CMD', CMDSchema);