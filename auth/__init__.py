from urllib.parse import urlsplit

import jwt
import sqlalchemy as sa
from flask_login import (
    current_user,
    login_user,
    logout_user,
)
from auth.forms import LoginForm, PasswordChangeForm, PasswordResetForm, SignupForm

from flask import Blueprint, current_app, flash, redirect, render_template, request
from extensions import db
from auth.email import send_password_reset_email
from models.user import User

bp = Blueprint("auth", __name__)


@bp.route("/logout")
def logout_ep():
    logout_user()
    return redirect("/")


@bp.route("/login", methods=["GET", "POST"])
def login_ep():
    if current_user.is_authenticated:
        return redirect("/")

    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            sa.Select(User).where(User.username == form.username.data)
        )

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect("/login")

        login_user(user)

        next_page = request.args.get("next")

        if not next_page or urlsplit(next_page).netloc != "":
            next_page = "/"

        return redirect(next_page)

    return render_template("login.html", form=form)


@bp.route("/signup", methods=["GET", "POST"])
def signup_ep():
    form = SignupForm()

    if form.validate_on_submit():
        flash("You are now signed up.")
        return redirect("/")

    return render_template("signup.html", form=form)


@bp.route("/password-reset", methods=["GET", "POST"])
def reset_passwd_ep():
    form = PasswordResetForm()

    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))

        if user:
            send_password_reset_email(user)

        flash("Check your email for password reset instructions")

    return render_template("reset_password.html", form=form)


@bp.route("/password-reset/<token>", methods=["GET", "POST"])
def change_passwd_ep(token):
    try:
        user_id = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )["user"]
    except:
        return redirect("/")

    user = db.session.get(User, user_id)
    assert user

    form = PasswordChangeForm()

    if form.validate_on_submit():
        assert form.password.data
        user.set_password(form.password.data)
        db.session.commit()

        flash("Your password was changed")
        return redirect("/login")

    return render_template("change_password.html", form=form)
