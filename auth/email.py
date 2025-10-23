from time import time
import jwt
from flask_mail import Message

from flask import current_app, render_template

from models.user import User
from extensions import mail


def send_mail(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(user: User):
    token = jwt.encode(
        {"user": user.id, "exp": time() + 60 * 10},
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )

    send_mail(
        "Reset your email",
        sender=current_app.config["ADMIN"],
        recipients=[user.email],
        text_body=render_template("email/password_reset.txt", user=user, token=token),
        html_body=render_template("email/password_reset.html", user=user, token=token),
    )
