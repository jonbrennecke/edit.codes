/**
 *
 * User Schema
 *
 */


var mongoose = require('mongoose'),
	Schema = mongoose.Schema,
	bcrypt = require('bcrypt');


// User Schema
var UserSchema = new Schema({

	name : { type : String, required : true },
	passwordHash : { type : String, required : true },
	email : { type : String, required : true },

});



// virtual get/set for the password hash
UserSchema.virtual('password')

	.get( function () {
		return this.__password
	})

	.set( function ( value ) {
		this.__password = value;
		var salt = bcrypt.genSaltSync( 10 );
		this.passwordHash = bcrypt.hashSync( value, salt );
	});


// validate a password by checking number of characters and 
// presence of number within the password
UserSchema.path('passwordHash').validate( function ( v ) {
	// TODO validate password

	if ( this.isNew && !this.__password ) {
		this.invalidate( 'password', 'required' );
	}
}, null);



// check the password against the hash using bcrypt's 'compareSync'
UserSchema.methods.checkPassword = function ( password ) {
	return bcrypt.compareSync( password, this.passwordHash );
}


// finally, export the user schema
module.exports = mongoose.model('User', UserSchema);