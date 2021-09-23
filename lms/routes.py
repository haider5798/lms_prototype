import os
import secrets
from PIL import Image
from flask import (Response, redirect, flash, render_template, url_for, request, session, send_file,
                   send_from_directory)
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import or_, and_

from lms import app, bcrypt, db, mail, UPLOAD_FOLDER, today
from lms.forms import (RegistrationForm, LoginForm, UpdateAccountForm, CreateNewAssignmentForm, CourseAssignedForm,
                       StudentEnrolmentForm, UserSearchForm, RequestResetForm, ResetPasswordForm,
                       AssignmentSubmissionForm,
                       CreateNewCourseForm, MarksEntryForm)
from lms.models import User, AssignmentSubmitted, NewAssignments, Course, EnrolledStudent
from flask_mail import Message
from lms import ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Check Credentials', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    ten_form = CourseAssignedForm()
    sen_form = StudentEnrolmentForm()
    courses = Course.query.all()
    courses_list = [(i.id, i.title) for i in courses]
    sen_form.title.choices = courses_list
    ten_form.title.choices = courses_list
    sum_details = {}
    if current_user.user_category == 'Admin':
        total_students = User.query.filter_by(user_category='Student').count()
        total_teachers = User.query.filter_by(user_category='Teacher').count()
        total_courses = Course.query.count()
        sum_details = {'Courses': total_courses, 'Students': total_students, 'Teachers': total_teachers}

    if current_user.user_category == 'Teacher':
        courses = Course.query.filter_by(assigned_to=current_user.username).all()
        if ten_form.validate_on_submit():
            course = Course.query.filter_by(id=ten_form.title.data).first()
            course.assigned_to = current_user.username
            db.session.flush()
            db.session.commit()
            return redirect(url_for('home'))
    elif current_user.user_category == 'Student':
        courses = []
        i = EnrolledStudent.query.filter_by(student_id=current_user.id).all()
        if i:
            for j in i:
                c = Course.query.filter_by(id=j.course_id).first()
                courses.append(c)
        if sen_form.validate_on_submit():
            student = EnrolledStudent(course_id=sen_form.title.data, student_id=current_user.id)
            db.session.add(student)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('home.html', title='Home', form=sen_form, form2=ten_form, courses=courses,
                           sum_details=sum_details)


@app.route('/course_management', methods=['GET', 'POST'])
@login_required
def course_management():
    cc_form = CreateNewCourseForm()
    headings = ['Course ID', 'Course Title', 'Assigned To', '']
    courses = Course.query.all()
    if cc_form.validate_on_submit():
        course = Course(title=cc_form.title.data)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('course_management'))
    return render_template('course_management.html', title='Course Management', form=cc_form, headings=headings,
                           data=courses)


@app.route('/account_management', methods=['GET', 'POST'])
@login_required
def account_management():
    reg_form = RegistrationForm()
    search_form = UserSearchForm()
    headings = ['Username', 'User Category', 'Email', '']
    data = User.query.all()
    if reg_form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(reg_form.password.data).decode('utf-8')
        user = User(name=reg_form.name.data, username=reg_form.username.data, email=reg_form.email.data,
                    address=reg_form.address.data, mobile_no=reg_form.mobile_no.data,
                    user_category=reg_form.user_category.data,
                    password=hashed_pass)

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('account_management'))
    return render_template('account_management.html', title='User Accounts Management', form=reg_form, data=data,
                           headings=headings)


@app.route('/register', methods=['GET', 'POST'])
def register():
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(reg_form.password.data).decode('utf-8')
        user = User(name=reg_form.name.data, username=reg_form.username.data, email=reg_form.email.data,
                    address=reg_form.address.data, mobile_no=reg_form.mobile_no.data,
                    password=hashed_pass, user_category=reg_form.user_category.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Account Registration', form=reg_form, )


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_assignment(file):
    random_hex = secrets.token_hex()
    _, f_ext = os.path.splitext(file.filename)
    assignment_fn = random_hex + f_ext
    assignment_path = os.path.join(app.root_path, UPLOAD_FOLDER, assignment_fn)
    file.save(assignment_path)
    return assignment_fn


@app.route('/detail_page/<course>/', methods=['GET', 'POST'])
@login_required
def detail_page(course):
    as_form = AssignmentSubmissionForm()
    na_form = CreateNewAssignmentForm()
    me_form = MarksEntryForm()
    headings = ['Assignment ID', 'Student Name', 'Plagiarism Percentage', 'Marks', '']
    sheadings = ['Assignment ID', 'Title', ' Due Date', 'Marks Obtained', '']
    exp_assignments = db.session.query(NewAssignments).filter(NewAssignments.due_date < today).all()
    if exp_assignments:
        for assignment in exp_assignments:
            assign = NewAssignments.query.get(assignment.id)
            db.session.delete(assign)
            db.session.commit()
    assignments = NewAssignments.query.filter_by(course=course).all()
    assignments_list = [(i.id, i.description) for i in assignments]
    as_form.assignment.choices = assignments_list
    data = AssignmentSubmitted.query.filter_by(course=course).all()
    data2 = NewAssignments.query.filter_by(course=course).all()

    if current_user.user_category == 'Student':
        if as_form.validate_on_submit():
            file_name = save_assignment(as_form.assignment_file.data)
            file = AssignmentSubmitted(student_username=current_user.name, course=course, assignment_file=file_name)
            db.session.add(file)
            db.session.commit()
            return redirect(url_for('detail_page', course=course))
    if current_user.user_category == 'Teacher':
        if na_form.validate_on_submit():
            if na_form.assignment_file.data:
                file_name = save_assignment(na_form.assignment_file.data)
                file = NewAssignments(description=na_form.description.data, due_date=na_form.due_date.data,
                                      course=course, assignment_file=file_name)
                db.session.add(file)
                db.session.commit()
                return redirect(url_for('detail_page', course=course))
        elif me_form.validate_on_submit():
            assignment = AssignmentSubmitted.query.filter_by(id=me_form.assignment_id.data).first()
            assignment.marks_obt = me_form.marks.data
            db.session.flush()
            db.session.commit()
            return redirect(url_for('detail_page', course=course))
    return render_template('detail_page.html', form=as_form, form2=na_form, meform=me_form, course=course,
                           headings=headings, data=data, data2=data2, sheadings=sheadings)


@app.route('/download-file/<filename>',  methods=['GET', 'POST'])
def download_file(filename):
    uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=filename)


# @app.route('/about')
# @login_required
# def about():
#     return render_template('about.html', title='About')


def save_picture(form_picture):
    random_hex = secrets.token_hex()
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    update_form = UpdateAccountForm()
    if update_form.validate_on_submit():
        if update_form.picture.data:
            picture_file = save_picture(update_form.picture.data)
            current_user.image_file = picture_file
        db.session.commit()
        # flash('Your account has been updated!', 'success')
        return redirect(url_for('user_profile'))
    elif request.method == 'GET':
        update_form.name.data = current_user.name
        update_form.email.data = current_user.email
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('user_profile.html', title='User Profile',
                           image_file=image_file, form=update_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/delete_user/<id>/', methods=['GET', 'POST'])
def delete_user(id):
    data = User.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('account_management'))


@app.route('/delete_course/<id>/', methods=['GET', 'POST'])
def delete_course(id):
    data = Course.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('course_management'))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='nadeem.haider34603@gmail.com',
                  recipients=[user.email])
    msg.body = f''' To reset you password, Visit the following link:
    {url_for('reset_token', token=token, _external=True)}
    If you did not make any request then ignore this Email.'''
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
    return render_template('reset_request.html', title='Reset Password', form=form)

#
# @app.route('/reset_password/<token>', methods=['GET', 'POST'])
# def reset_token(token):
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     user = user.verify_reset_token(token)
#     if user is None:
#         flash('Token is Invalid or Expired', 'Danger')
#         return redirect(url_for('reset_request'))
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         user.password = hashed_pass
#         db.session.commit()
#         flash(f'Your Password has been Updated.', 'success')
#         return redirect(url_for('login'))
#     return render_template('reset_password.html', title='Reset Password', form=form)
