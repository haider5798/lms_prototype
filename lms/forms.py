from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from lms.models import User, Assignment


class RegistrationForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=5, max=20)],
                       render_kw={"placeholder": "i.e Zaberdast Khan"})
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "i.e Jhonny"})

    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={"placeholder": "i.e abc@example.com"})
    address = StringField('Address', validators=[DataRequired()], render_kw={"placeholder": "i.e Lahore, Pakistan"})
    mobile_no = StringField('Mobile No', validators=[DataRequired(), Length(min=11, max=11)],
                            render_kw={"placeholder": "0300 0000000"})
    course = SelectField('Course', choices=['Calculas', 'Computer Science', 'Political Studies', 'English',
                                            'Urdu Adab', 'None'])
    user_category = SelectField('User Category', choices=['Admin', 'Teacher', 'Student'])
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')],
                                     render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Register')

    @staticmethod
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is Already taken. Please choose different Username')

    @staticmethod
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is Already taken. Please choose different Email')


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Jhonny"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UserSearchForm(FlaskForm):
    search_box = StringField('username',
                             validators=[DataRequired()], render_kw={"placeholder": "Username"})
    search = SubmitField('Search')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={"placeholder": "i.e abc@example.com"})
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email, user_category):
        user = user_category.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no Account against this Email. You must Register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')],
                                     render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Reset Password')


class AssignmentSubmissionForm(FlaskForm):
    assignment = FileField('Select Assignment File', validators=[FileAllowed(['pdf', 'docx'])])
    submit = SubmitField('Submit')

    def validate_submission(self):
        if current_user:
            user = Assignment.query.filter_by(username=current_user.name).first()
            if user:
                raise ValidationError('Assignment has already been submitted.')
