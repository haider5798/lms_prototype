import os
import secrets
from flask import current_app


def save_assignment(file):
    random_hex = secrets.token_hex()
    _, f_ext = os.path.splitext(file.filename)
    assignment_fn = random_hex + f_ext
    assignment_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], assignment_fn)
    file.save(assignment_path)
    return assignment_fn