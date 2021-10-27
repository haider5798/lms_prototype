from lms import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile_no = db.Column(db.String(120), unique=True, nullable=True)
    address = db.Column(db.String(20), unique=False, nullable=True)
    user_category = db.Column(db.String(20), unique=False, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.name}', '{self.user_category}', '{self.email}')"


class AssignmentSubmitted(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, nullable=False)
    student_username = db.Column(db.String(20), unique=False, nullable=False)
    course = db.Column(db.String(20), unique=False, nullable=False)
    plag_percentage = db.Column(db.Integer, nullable=True)
    plag_report = db.Column(db.String(50), unique=True, nullable=True)
    teacher_comments = db.Column(db.String(250), nullable=True)
    marks_obt = db.Column(db.Integer, nullable=True)
    assignment_file = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"SubmittedAssignment('{self.course}', '{self.student_username}', '{self.plag_percentage}')"


class NewAssignments(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(20), unique=False, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    course = db.Column(db.String(20), unique=False, nullable=False)
    assignment_file = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"NewAssignment('{self.description}', '{self.due_date}')"


class Course(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), unique=True, nullable=False)
    assigned_to = db.Column(db.String(20), unique=False, nullable=True)

    def __repr__(self):
        return f"Course('{self.title}', '{self.assigned_to}')"


class EnrolledStudent(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, unique=False, nullable=False)
    student_id = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return f"EnrolledStudent('{self.course_id}', '{self.student_id}')"
