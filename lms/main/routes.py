from flask import redirect, flash, render_template, url_for, Blueprint
from flask_login import current_user, login_required
from lms import bcrypt, db
from lms.main.forms import CourseAssignedForm, StudentEnrolmentForm, CreateNewCourseForm, RegistrationForm, UserSearchForm
from lms.models import User, Course, EnrolledStudent

main = Blueprint('main', __name__)


@main.route('/home', methods=['GET', 'POST'])
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
            flash('Course Assigned Successfully', 'success')
            return redirect(url_for('main.home'))
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
            flash('Student Enrollment Successful', 'success')
            return redirect(url_for('main.home'))
    return render_template('home.html', title='Home', form=sen_form, form2=ten_form, courses=courses,
                           sum_details=sum_details)


@main.route('/course_management', methods=['GET', 'POST'])
@login_required
def course_management():
    cc_form = CreateNewCourseForm()
    headings = ['Course ID', 'Course Title', 'Assigned To', '']
    courses = Course.query.all()
    if cc_form.validate_on_submit():
        course = Course(title=cc_form.title.data)
        db.session.add(course)
        db.session.commit()
        flash('Course Created!', 'success')
        return redirect(url_for('main.course_management'))
    return render_template('course_management.html', title='Course Management', form=cc_form, headings=headings,
                           data=courses)


@main.route('/account_management', methods=['GET', 'POST'])
def account_management():
    reg_form = RegistrationForm()
    search_form = UserSearchForm()
    headings = ['Username', 'User Category', 'Email', '']
    data = User.query.all()
    data.sort(key=lambda x: x.id, reverse=True)
    if reg_form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(reg_form.password.data).decode('utf-8')
        user = User(name=reg_form.name.data, username=reg_form.username.data, email=reg_form.email.data,
                    address=reg_form.address.data, mobile_no=reg_form.mobile_no.data,
                    user_category=reg_form.user_category.data,
                    password=hashed_pass)

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.account_management'))
    return render_template('account_management.html', title='User Accounts Management', form=reg_form, data=data,
                           headings=headings, search_form=search_form)


@main.route('/delete_user/<id>/', methods=['GET', 'POST'])
def delete_user(id):
    try:
        data = User.query.get(id)
        db.session.delete(data)
        db.session.commit()
        flash('User Deleted!', 'success')
        return redirect(url_for('main.account_management'))
    except Exception as E:
        print(type(E).__name__)
        flash('Something Went Wrong.\nPlease Check Logs for further details', 'Danger')


# @app.route('/about')
# @login_required
# def about():
#     return render_template('about.html', title='About')
