from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, InputRequired
from lms.models import User, AssignmentSubmitted, NewAssignments, Course, EnrolledStudent
from wtforms.fields.html5 import DateField
from lms import ALLOWED_EXTENSIONS


class RegistrationForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=5, max=20)],
                       render_kw={"placeholder": "i.e Zaberdast Khan"})
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "i.e Jhonny"})

    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={"placeholder": "i.e abc@example.com"})
    address = StringField('Address', validators=[DataRequired()], render_kw={"placeholder": "i.e Lahore, Pakistan"})
    mobile_no = StringField('Mobile No', validators=[Length(min=11, max=11)],
                            render_kw={"placeholder": "03000000000"})
    user_category = SelectField('User Category', choices=['Admin', 'Student', 'Teacher'])
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')],
                                     render_kw={"placeholder": "Confirm Password"})
    register = SubmitField('Register')

    @staticmethod
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is Already taken. Please choose different Username.')

    @staticmethod
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is Already taken. Please choose different Email.')

    @staticmethod
    def validate_mobile_no(self, mobile_no):
        user = User.query.filter_by(mobile_no=mobile_no.data).first()
        if user:
            raise ValidationError('Mobile No is Associated with different Account, Please Recheck.')


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember Me')
    login = SubmitField('Login')


class UserSearchForm(FlaskForm):
    search_box = StringField('username',
                             validators=[DataRequired()], render_kw={"placeholder": "Username"})
    search = SubmitField('Search')


class UpdateAccountForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    @staticmethod
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    @staticmethod
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={"placeholder": "i.e abc@example.com"})
    submit = SubmitField('Request Password Reset')

    @staticmethod
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
    assignment = SelectField('Assignment Title', validators=[InputRequired()])
    assignment_file = FileField('Select Assignment File', validators=[FileAllowed(ALLOWED_EXTENSIONS)])
    upload_assignment = SubmitField('Upload')

    @staticmethod
    def validate_assignment(self, assignment):
        result = AssignmentSubmitted.query.filter_by(student_username=current_user.name,
                                                     assignment_id=assignment.data).first()
        if result:
            raise ValidationError('Assignment Submitted')


class CreateNewAssignmentForm(FlaskForm):
    description = StringField('Title', validators=[DataRequired(), Length(min=5, max=50)])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    assignment_file = FileField('File', validators=[FileAllowed(ALLOWED_EXTENSIONS)])
    create_assignment = SubmitField('Post Assignment')


class CreateNewCourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(min=5, max=25)])
    create_course = SubmitField('Create')

    @staticmethod
    def validate_title(self, title):
        course = Course.query.filter_by(title=title.data).first()
        if course:
            raise ValidationError('Course Exists')


class CourseAssignedForm(FlaskForm):
    title = SelectField('Course Title', validators=[InputRequired()])
    assign_course = SubmitField('Enroll')

    @staticmethod
    def validate_title(self, title):
        data = Course.query.filter_by(id=title.data[0]).first()
        if data:
            if data.assigned_to:
                raise ValidationError('Course is already Assigned')


class StudentEnrolmentForm(FlaskForm):
    title = SelectField('Course Title', validators=[InputRequired()])
    enroll_student = SubmitField('Enroll')

    @staticmethod
    def validate_title(self, title):
        data = EnrolledStudent.query.filter_by(course_id=title.data[0]).all()
        for d in data:
            if d.student_id == current_user.id:
                raise ValidationError('Already Enrolled in this Course')


class MarksEntryForm(FlaskForm):
    assignment_id = StringField('Assignment ID', validators=[DataRequired()])
    marks = IntegerField('Enter Marks', validators=[InputRequired()])
    submit_marks = SubmitField('Submit')
