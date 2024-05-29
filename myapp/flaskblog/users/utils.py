import hmac
import hashlib
import time
import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = generate_reset_token(user)
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)




def generate_reset_token(user, expires_in=600):
    secret_key = current_app.config['SECRET_KEY']
    timestamp = int(time.time())
    message = f"{user.id}{timestamp}".encode('utf-8')
    token = hmac.new(secret_key.encode('utf-8'), message, hashlib.sha256).hexdigest()
    return f"{user.id}:{timestamp}:{token}"

def verify_reset_token(token):
    try:
        user_id, timestamp, token_hash = token.split(':')
        timestamp = int(timestamp)
    except (ValueError, IndexError):
        return None

    if time.time() > timestamp + 600:
        return None

    user = User.query.get(user_id)
    if user is None:
        return None

    secret_key = current_app.config['SECRET_KEY']
    message = f"{user.id}{timestamp}".encode('utf-8')
    expected_hash = hmac.new(secret_key.encode('utf-8'), message, hashlib.sha256).hexdigest()

    if hmac.compare_digest(expected_hash, token_hash):
        return user
    return None
