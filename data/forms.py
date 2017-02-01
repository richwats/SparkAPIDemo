### WTF Form Definitions ###

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, BooleanField, TextAreaField, FieldList, SelectField, HiddenField, FileField, SelectMultipleField, RadioField
from wtforms.validators import InputRequired, EqualTo, Optional, Email, Length, Regexp, ValidationError



class ContactUs(FlaskForm):
    
    firstname = StringField('First Name',
                           description="Please enter your last name",
                           validators=[InputRequired()],
                           render_kw = {'placeholder':'Bob'}
                           )
    
    lastname = StringField('Last Name',
                           description="Please enter your last name",
                           validators=[InputRequired()],
                           render_kw = {'placeholder':'Smith'}
                           )
    
    email = StringField('Email Address',
                           description="Please enter your email address",
                           validators=[InputRequired(), Email()],
                           render_kw = {'placeholder':'bob@test.com'}
                           )
    mobile = StringField('Mobile Number',
                           description="(Optional) Please enter your mobile number",
                           validators=[Optional(), Regexp("^\+\d+$", flags=0, message="Please enter mobile number in +E164 format (i.e. +61412345678)")],
                           render_kw = {'placeholder':'+61412345678'}
                           )
    message = TextAreaField('Message',
                            description="How can we help?",
                            render_kw = {'rows':10}
                            )
    
    submit = SubmitField('Submit Message')
    

# class RegisterUser(FlaskForm):
#     
#     firstname = StringField('First Name',
#                            description="Please enter your last name",
#                            validators=[InputRequired()],
#                            render_kw = {'placeholder':'Bob'}
#                            )
#     
#     lastname = StringField('Last Name',
#                            description="Please enter your last name",
#                            validators=[InputRequired()],
#                            render_kw = {'placeholder':'Smith'}
#                            )
#     
#     email = StringField('Email Address',
#                            description="Please enter your email address",
#                            validators=[InputRequired(), Email()],
#                            render_kw = {'placeholder':'bob@test.com'}
#                            )
#     mobile = StringField('Mobile Number',
#                            description="(Optional) Please enter your mobile number",
#                            validators=[Optional(), Regexp("^\+\d+$", flags=0, message="Please enter mobile number in +E164 format (i.e. +61412345678)")],
#                            render_kw = {'placeholder':'+61412345678'}
#                            )
# 
#     submit = SubmitField('Register User')

class ChatLogin(FlaskForm):
    
    call = HiddenField('call')
    
    firstname = StringField('First Name',
                           description="Please enter your last name",
                           validators=[InputRequired()],
                           render_kw = {'placeholder':'Bob'}
                           )
    
    lastname = StringField('Last Name',
                           description="Please enter your last name",
                           validators=[InputRequired()],
                           render_kw = {'placeholder':'Smith'}
                           )
    
    email = StringField('Email Address',
                           description="Please enter your email address",
                           validators=[InputRequired(), Email()],
                           render_kw = {'placeholder':'bob@test.com'}
                           )
    mobile = StringField('Mobile Number',
                           description="(Optional) Please enter your mobile number",
                           validators=[Optional(), Regexp("^\+\d+$", flags=0, message="Please enter mobile number in +E164 format (i.e. +61412345678)")],
                           render_kw = {'placeholder':'+61412345678'}
                           )

    # No Submit - Use Button in modal window #
    
class NewTeam(FlaskForm):
    
    teamName = StringField('Team Name',
                           description="Please enter the name for the new Cisco Spark team.",
                           validators=[InputRequired()],
                           render_kw = {'placeholder':'Customer Representatives'}
                           )
    
    submit = SubmitField('Add New Team')
    