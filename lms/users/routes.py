from flask import redirect, flash, render_template, url_for, request, Blueprint
from flask_login import login_required, login_user, logout_user, current_user
from lms import bcrypt, db
from lms.users.forms import LoginForm, UpdateAccountForm, RequestResetForm
from lms.main.forms import RegistrationForm
from lms.models import User
from lms.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


@users.route('/', methods=['GET', 'POST'])
@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Check Credentials', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route('/register', methods=['GET', 'POST'])
def register():
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(reg_form.password.data).decode('utf-8')
        user = User(name=reg_form.name.data, username=reg_form.username.data, email=reg_form.email.data,
                    address=reg_form.address.data, mobile_no=reg_form.mobile_no.data,
                    password=hashed_pass, user_category=reg_form.user_category.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Account Registration', form=reg_form)


@users.route('/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    update_form = UpdateAccountForm()
    if update_form.validate_on_submit():
        if update_form.picture.data:
            picture_file = save_picture(update_form.picture.data)
            current_user.image_file = picture_file
        db.session.commit()
        flash('Your Profile has been updated!', 'success')
        return redirect(url_for('users.user_profile'))
    elif request.method == 'GET':
        update_form.name.data = current_user.name
        update_form.email.data = current_user.email
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('user_profile.html', title='User Profile',
                           image_file=image_file, form=update_form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
    return render_template('reset_request.html', title='Reset Password', form=form)

#
# @app.route('/reset_password/<token>', methods=['GET', 'POST'])
# def reset_token(token):
#     if current_user.is_authenticated:
#         return redirect(url_for('main.home'))
#     users = users.verify_reset_token(token)
#     if users is None:
#         flash('Token is Invalid or Expired', 'Danger')
#         return redirect(url_for('reset_request'))
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         users.password = hashed_pass
#         db.session.commit()
#         flash(f'Your Password has been Updated.', 'success')
#         return redirect(url_for('login'))
#     return render_template('reset_password.html', title='Reset Password', form=form)
