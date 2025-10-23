from flask import Flask
from logging.handlers import SMTPHandler
import logging
import errors
import auth as authn
from models.user import User
import main
import extensions

def create_app(default_config = "default_config"):
    app = Flask(__name__)

    app.config.from_object(default_config)
    app.config.from_prefixed_env()

    extensions.db.init_app(app)
    extensions.migrate.init_app(app, extensions.db)
    extensions.login_mgr.init_app(app)
    extensions.login_mgr.login_view = "auth.login_ep"
    extensions.mail.init_app(app)

    app.register_blueprint(errors.bp)
    app.register_blueprint(authn.bp, url_prefix="/auth")
    app.register_blueprint(main.bp)

    if not app.debug and app.config.get("MAIL_SERVER"):
        auth = None
        if app.config.get("MAIL_USERNAME") and app.config.get("MAIL_PASSWORD"):
            auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])

        secure = None
        if app.config.get("MAIL_USE_TLS"):
            secure = ()

        handler = SMTPHandler(
            mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
            fromaddr="no-reply@" + app.config["MAIL_SERVER"],
            toaddrs=[app.config["ADMIN"]],
            subject="Error in Microblogging App",
            credentials=auth,
            secure=secure,
        )

        handler.setLevel(logging.ERROR)
        app.logger.addHandler(handler)

    @extensions.login_mgr.user_loader
    def load_user(id):# -> Any:
        return extensions.db.session.get(User, int(id))

    return app
