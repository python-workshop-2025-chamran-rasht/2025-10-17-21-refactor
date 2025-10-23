from flask import Blueprint, render_template
from extensions import db

bp = Blueprint('errors', __name__)

@bp.app_errorhandler(404)
def not_found_handler(_):
    return render_template("404.html"), 404

@bp.app_errorhandler(500)
def error_handler(_):
    db.session.rollback()
    return render_template("500.html"), 500
