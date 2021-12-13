from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from lms.models import User, Course, EnrolledStudent


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


class UserSearchForm(FlaskForm):
    search_box = StringField('username',
                             validators=[DataRequired()], render_kw={"placeholder": "Username"})
    search = SubmitField('Search')


class CreateNewCourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(min=5, max=25)])
    create_course = SubmitField('Create')

    @staticmethod
    def validate_title(self, title):
        course = Course.query.filter_by(title=title.data).first()
        if course:
            raise ValidationError('Course Exists')


class CourseAssignedForm(FlaskForm):
    title = SelectField('Course Title', validators=[DataRequired()])
    assign_course = SubmitField('Enroll')

    @staticmethod
    def validate_title(self, title):
        data = Course.query.filter_by(id=title.data[0]).first()
        if data:
            if data.assigned_to:
                raise ValidationError('Course is already Assigned')


class StudentEnrolmentForm(FlaskForm):
    title = SelectField('Course Title', validators=[DataRequired()])
    enroll_student = SubmitField('Enroll')

    @staticmethod
    def validate_title(self, title):
        data = EnrolledStudent.query.filter_by(course_id=title.data[0]).all()
        for d in data:
            if d.student_id == current_user.id:
                raise ValidationError('Already Enrolled in this Course')