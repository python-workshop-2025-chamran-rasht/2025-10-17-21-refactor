from datetime import datetime, timezone
from flask import Blueprint, render_template
from flask_login import current_user, login_required
import sqlalchemy as sa
from extensions import db
from models.user import User


bp = Blueprint('main', __name__)

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@bp.route("/")
@login_required
def index_ep():
    return render_template("index.html")


@bp.route("/user/<username>")
@login_required
def user_ep(username: str):
    user = db.first_or_404(sa.select(User).where(User.username == username))

    posts = [
        {"author": user, "content": "Test post 1"},
        {"author": user, "content": "Test post 2"},
    ]

    return render_template("profile.html", user=user, posts=posts)
