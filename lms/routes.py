import datetime
import os
import secrets
from PIL import Image
from flask import (Response, redirect, flash, render_template, url_for, request, session)
from flask_login import login_user, logout_user, current_user, login_required

from lms import app, bcrypt, db, mail
from lms.forms import (RegistrationForm, LoginForm, UpdateAccountForm, CreateNewAssignment, CourseAssigned,
                       StudentEnrolment, UserSearchForm, RequestResetForm, ResetPasswordForm, AssignmentSubmissionForm,
                       CreateNewCourse)
from lms.models import User, AssignmentSubmitted, NewAssignments, Course, EnrolledStudent
from flask_mail import Message


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
    en_form = CourseAssigned()
    sen_form = StudentEnrolment()
    courses = Course.query.all()
    courses_list = [(i.id, i.title) for i in courses]
    en_form.title.choices = courses_list
    # sen_form.title.choices = courses_list
    if current_user.user_category == 'Teacher':
        courses = Course.query.filter_by(assigned_to=current_user.username).all()
        if en_form.validate_on_submit():
            print(en_form.title.data)
            course = Course.query.filter_by(id=en_form.title.data).first()
            print(course)
            course.assigned_to = current_user.username
            db.session.flush()
            db.session.commit()
            return redirect(url_for('home'))
    elif current_user.user_category == 'Student':
        courses = EnrolledStudent.query.filter_by(student_id=current_user.id).all()
        if sen_form.validate_on_submit():
            student = EnrolledStudent(course_id=sen_form.title.data, student_id=current_user.id)
            db.session.add(student)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('home.html',  title='Home', form=en_form, form2=sen_form, courses=courses)


@app.route('/course_management', methods=['GET', 'POST'])
@login_required
def course_management():
    cc_form = CreateNewCourse()
    headings = ['Course ID', 'Course Title', 'Assigned To', '        ']
    courses = Course.query.all()
    if cc_form.validate_on_submit():
        course = Course(title=cc_form.title.data)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('course_management'))
    return render_template('course_management.html',  title='Course Management', form=cc_form, headings=headings, data=courses)


@app.route('/account_management', methods=['GET', 'POST'])
def account_management():
    reg_form = RegistrationForm()
    search_form = UserSearchForm()
    headings = ['Username', 'User Category', 'Email', '          ']
    data = User.query.all()
    if reg_form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(reg_form.password.data).decode('utf-8')
        user = User(name=reg_form.name.data, username=reg_form.username.data, email=reg_form.email.data,
                    address=reg_form.address.data, mobile_no=reg_form.mobile_no.data, user_category=reg_form.user_category.data,
                    password=hashed_pass)

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('account_management'))
    return render_template('account_management.html', title='User Accounts Management', form=reg_form, data=data,
                           search_form=search_form, headings=headings)


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
        return redirect(url_for('register'))
    return render_template('register.html', title='Account Registration', form=reg_form, )


def save_assignment(file):
    random_hex = secrets.token_hex()
    _, f_ext = os.path.splitext(file.filename)
    file_fn = random_hex + f_ext
    file_path = os.path.join(app.root_path, 'static/assignment_files', file_fn)


@app.route('/detail_page/<course>/', methods=['GET', 'POST'])
def detail_page(course):
    as_form = AssignmentSubmissionForm()
    na_form = CreateNewAssignment()
    headings = ['Assignment ID', 'Student Name', 'Plagiarism Percentage', '              ', '             ']
    sheadings = ['Assignment ID', 'Assignment Name', ' Marks Obtained']
    data = AssignmentSubmitted.query.all()
    if as_form.validate_on_submit():
        if as_form.assignment.data:
            save_assignment(as_form.assignment.data)
            file = AssignmentSubmitted(student_username=current_user.name, course=course, assignment_file=as_form.assignment.data)
            db.session.add(file)
            db.session.commit()
            print('Here2')
            return redirect(url_for('detail_page'))
    if na_form.validate_on_submit():
        return redirect(url_for('detail_page'))
    return render_template('detail_page.html', form=as_form, form2=na_form, course=course, headings=headings, data=data, sheadings=sheadings)


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


@app.route('/delete/<id>/', methods=['GET', 'POST'])
def delete(id):
    data = User.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('account_management'))


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
