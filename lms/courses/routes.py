import os
from flask import redirect, flash, render_template, url_for, send_from_directory, Blueprint, current_app
from flask_login import current_user, login_required
from lms import db, today
from lms.text_matcher.text_matcher import cli
from lms.courses.utils import save_assignment
from lms.courses.forms import (CreateNewAssignmentForm, AssignmentSubmissionForm, MarksEntryForm, TeacherComment,
                               AssignmentSelection)
from lms.models import AssignmentSubmitted, NewAssignments, Course

courses = Blueprint('courses', __name__)


@courses.route('/detail_page/<course>/', methods=['GET', 'POST'])
@login_required
def detail_page(course):
    as_form = AssignmentSubmissionForm()
    na_form = CreateNewAssignmentForm()
    me_form = MarksEntryForm()
    tc_form = TeacherComment()
    as_select_form = AssignmentSelection()
    sa_headings = ['S.No', 'Student Username', 'Plagiarism', 'Marks', 'Comments', '']
    na_headings = ['S.No', 'Assignment Title', 'Due Date', '']
    sheadings = ['S.No', 'Title', ' Due Date', 'Marks Obtained', 'Plagiarism', "Teacher's Comments", '']
    active_assignments = db.session.query(NewAssignments).filter(NewAssignments.due_date >= today).all()
    all_assignments = db.session.query(NewAssignments)
    all_assign_list = [(i.id, i.description) for i in all_assignments]
    assignments_list = [(i.id, i.description) for i in active_assignments]
    as_form.assignment.choices = assignments_list
    as_select_form.title.choices = all_assign_list
    data = AssignmentSubmitted.query.filter_by(course=course).all()
    # data.sort(key=lambda x: x.id, reverse=True)   # Sort the data so that each new entry show upfront
    data2 = NewAssignments.query.filter_by(course=course).all()
    # data2.sort(key=lambda x: x.id, reverse=True)  # # Sort the data so that each new entry show upfront
    sas_ids = [i.assignment_id for i in data]

    if current_user.user_category == 'Student':
        if as_form.validate_on_submit():
            file_name = save_assignment(as_form.assignment_file.data)
            file = AssignmentSubmitted(assignment_id=as_form.assignment.data, student_username=current_user.username,
                                       course=course, assignment_file=file_name)
            db.session.add(file)
            db.session.commit()
            flash('Assignment Submit Successfully!', 'success')
            return redirect(url_for('courses.detail_page', course=course))
    if current_user.user_category == 'Teacher':
        if na_form.validate_on_submit():
            if na_form.assignment_file.data:
                file_name = save_assignment(na_form.assignment_file.data)
                file = NewAssignments(description=na_form.description.data, due_date=na_form.due_date.data,
                                      course=course, assignment_file=file_name)
                db.session.add(file)
                db.session.commit()
                flash('Assignment Created Successfully!', 'success')
            return redirect(url_for('courses.detail_page', course=course))
        elif me_form.validate_on_submit():
            assignment = AssignmentSubmitted.query.filter_by(id=me_form.assignment_id.data).first()
            assignment.marks_obt = me_form.marks.data
            db.session.flush()
            db.session.commit()
            return redirect(url_for('courses.detail_page', course=course))
        elif tc_form.validate_on_submit():
            assignment = AssignmentSubmitted.query.filter_by(id=tc_form.assignment_id.data).first()
            assignment.teacher_comments = tc_form.teacher_comment.data
            db.session.flush()
            db.session.commit()
            flash('Teachers Commented Successfully!', 'success')
            return redirect(url_for('courses.detail_page', course=course))
        elif as_select_form.validate_on_submit():
            submitted_assignments = AssignmentSubmitted.query.filter_by(id=as_select_form.title.data).all()
            flash('Success!', 'success')
            return redirect(url_for('courses.detail_page', course=course, data=submitted_assignments))
    return render_template('detail_page.html', form=as_form, form2=na_form, meform=me_form, tcform=tc_form,
                           as_select_form=as_select_form, course=course, sa_headings=sa_headings,
                           na_headings=na_headings, data=data, data2=data2, sas_ids=sas_ids, sheadings=sheadings)


@courses.route('/download-file/<filename>', methods=['GET', 'POST'])
def download_file(filename):
    directory = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
    print(directory)
    return send_from_directory(directory=directory, filename=filename)


@courses.route('/download_report_file/<filename>', methods=['GET', 'POST'])
def download_report_file(filename):
    directory = os.path.join(current_app.root_path, current_app.config['PLAG_REPORT'])
    flash(f'Action Successful.', 'Success')
    return send_from_directory(directory=directory, filename=filename)


@courses.route('/plag_check/<course>/<filename>/<id>/', methods=['GET', 'POST'])
def plag_check(course, filename, id):
    try:
        uploads = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
        database = os.path.join(current_app.root_path, current_app.config['DATABASE_FOLDER'])
        plag_report_file, plag_percentage = cli(uploads + filename, database + 'jlskdjflskjdflksjdfklsjdfjkl.pdf')
        if plag_report_file:
            assign = AssignmentSubmitted.query.get(id)
            assign.plag_report = plag_report_file
            if plag_percentage:
                assign.plag_percentage = plag_percentage
            db.session.flush()
            db.session.commit()
            flash('Plagiarism Check Successful!', 'success')
            return redirect(url_for('courses.detail_page', course=course))
        else:
            flash('Something Went Wrong\n Please Check Logs to further Details!', 'Danger')
    except Exception as E:
        print(type(E).__name__)
        return redirect(url_for('courses.detail_page', course=course))


@courses.route('/delete_course/<id>/', methods=['GET', 'POST'])
def delete_course(id):
    data = Course.query.get(id)
    db.session.delete(data)
    db.session.commit()
    flash('Course Deleted!', 'success')
    return redirect(url_for('main.course_management'))


@courses.route('/delete_assignment/<id>/<course>/', methods=['GET', 'POST'])
def delete_assignment(course, id):
    data = NewAssignments.query.get(id)
    db.session.delete(data)
    db.session.commit()
    flash('Assignment Deleted!', 'success')
    return redirect(url_for('courses.detail_page', course=course))
