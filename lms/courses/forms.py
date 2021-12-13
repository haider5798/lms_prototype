from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, SubmitField, SelectField, IntegerField, validators, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, InputRequired
from lms.models import AssignmentSubmitted
from wtforms.fields.html5 import DateField
from lms import ALLOWED_EXTENSIONS, today


class AssignmentSubmissionForm(FlaskForm):
    assignment = SelectField('Assignment Title', validators=[InputRequired()])
    assignment_file = FileField('Select Assignment File', validators=[FileAllowed(ALLOWED_EXTENSIONS)])
    upload_assignment = SubmitField('Upload')

    @staticmethod
    def validate_assignment(self, assignment):
        result = AssignmentSubmitted.query.filter_by(student_username=current_user.username,
                                                     assignment_id=assignment.data).first()
        if result:
            raise ValidationError('Assignment Submitted')

    @staticmethod
    def validate_assignment_file(self, assignment_file):
        if assignment_file.data is None:
            raise ValidationError('Are You Fucking Nuts! No File Selected')


class CreateNewAssignmentForm(FlaskForm):
    description = StringField('Title', validators=[DataRequired(), Length(min=5, max=50)])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    assignment_file = FileField('File', validators=[FileAllowed(ALLOWED_EXTENSIONS)])
    create_assignment = SubmitField('Post Assignment')

    @staticmethod
    def validate_due_date(self, due_date):
        if due_date.data < today:
            raise ValidationError('Invalid Date. Please Select A Valid Date')

    @staticmethod
    def validate_assignment_file(self, assignment_file):
        if assignment_file.data is None:
            raise ValidationError('Are You Fucking Nuts! No File Selected')


class MarksEntryForm(FlaskForm):
    assignment_id = StringField('Assignment ID', validators=[DataRequired()])
    marks = IntegerField('Enter Marks', validators=[InputRequired()])
    submit_marks = SubmitField('Submit')


class TeacherComment(FlaskForm):
    assignment_id = StringField('Assignment ID', validators=[DataRequired()])
    teacher_comment = TextAreaField('Comments', [validators.optional(), validators.length(max=300)])
    submit_comment = SubmitField('Submit')


class AssignmentSelection(FlaskForm):
    title = SelectField('Assignment', validators=[InputRequired()])
    this_assignment = SubmitField('Show')