import os
import secrets
from flask import current_app, url_for
from PIL import Image
from flask_mail import Message
from lms import mail


def save_picture(form_picture):
    random_hex = secrets.token_hex()
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='nadeem.haider34603@gmail.com',
                  recipients=[user.email])
    msg.body = f''' To reset you password, Visit the following link:
    {url_for('users.reset_token', token=token, _external=True)}
    If you did not make any request then ignore this Email.'''
    mail.send(msg)
