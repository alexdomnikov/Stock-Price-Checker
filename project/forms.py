
# Third-party libraries
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError


# Create an authentication form - we're going to use this for both registering and logging in
class AuthForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
    
    login_submit = SubmitField("Login")
    register_submit = SubmitField("Register")

    def validate_username(self, username):
        # We'll use this during a registration attempt
        # We'll handle the login directly in the login route
        pass