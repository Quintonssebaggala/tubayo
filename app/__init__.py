import os
from flask import Flask, request, render_template
from config import configure_app
from app.utils import get_instance_folder_path
from app.cache import cache
from flask_mail import Mail
from app.data.models import db, login_manager, User, Experience, Flyer, OAuth
from flask_mail import Message

from social_flask_sqlalchemy.models import init_social

import logging
import flask_whooshalchemy as whooshalchemy
from logging.handlers import SMTPHandler, RotatingFileHandler
from sqlalchemy.sql import func
from flask_login import current_user
from werkzeug.contrib.fixers import ProxyFix
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend

mail = Mail()

app = Flask(__name__, 
	instance_path=get_instance_folder_path(), 
	instance_relative_config=True, template_folder='templates')

configure_app(app)
app.wsgi_app = ProxyFix(app.wsgi_app)
# Lazy initialization
cache.init_app(app)
db.init_app(app)
mail.init_app(app)
login_manager.init_app(app)


# init_social(app, session)


whooshalchemy.whoosh_index(app, Flyer)

# logging configs

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['TUBAYO_ADMIN'], subject='Tubayo Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
            os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/tubayolog.log', maxBytes=10240,
                                           backupCount=10)
    file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Tubayo startup')


@app.route('/about')
def about():
    app.logger.warning('A warning message is sent.')
    app.logger.error('An error message is sent.')
    app.logger.info('Information: 3 + 2 = %d', 5)
    return "about"

@app.route("/send")
def send():
   msg = Message('Hello', sender = 'ssebaggalaq@gmail.com', recipients = ['quinton.ssebaggala@gmail.com'])
   msg.body = "yo quinton"
   mail.send(msg)
   return "Sent"

# error handling

@app.errorhandler(404)
def page_not_found(error):
	app.logger.error('Page not found: %s', (request.path))
	return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', (error))
    return render_template('errors/500.html'), 500

# @app.errorhandler(403)
# def internal_server_error(error):
#     app.logger.error('Server Error: %s', (error))
#     return render_template('errors/500.html'), 403

# @app.errorhandler(410)
# def internal_server_error(error):
#     app.logger.error('Server Error: %s', (error))
#     return render_template('errors/500.html'), 410

# @app.errorhandler(Exception)
# def unhandled_exception(e):
#     app.logger.error('Unhandled Exception: %s', (e))
#     return render_template('errors/500.html'), 500

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = func.now()
        db.session.commit()
    app.jinja_env.cache = {}


@app.route('/send-mail/')
def send_mail():
	try:
		msg = Message("Hello",
		                  sender="from@example.com",
		                  recipients=["to@example.com"])
		msg.body = "testing"
		msg.html = "<b>testing</b>"        
		mail.send(msg)
		return 'Mail sent!'
	except Exception as e:
		return(str(e))


blueprint = make_google_blueprint(
    client_id="300005151407-f0v5ujvhvgprdkadi5uccpuqdkenvq6b.apps.googleusercontent.com",
    client_secret="ZEujtphXBAxiPTrfU7xymfFH",
    scope=["profile", "email"]
)

facebook_blueprint = make_facebook_blueprint(
    client_id="266065757264257",
    client_secret="e78e404f75b71bbb293d378218891836",
    scope=['public_profile','user_friends','email']
)


# setup SQLAlchemy backend
blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)
facebook_blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)

#flask register_blueprint()

from app.main import main
from app.admin import admin
from app.auth import auth
from social_flask.routes import social_auth

app.register_blueprint(main)
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(social_auth)
app.register_blueprint(blueprint, url_prefix="/login")
app.register_blueprint(facebook_blueprint, url_prefix="/login") 

#redirect views
login_manager.login_view = 'auth.login'

