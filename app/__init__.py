from flask import Flask, request, render_template
from config import configure_app
from app.utils import get_instance_folder_path
from app.cache import cache
from app.data.models import db


import logging

app = Flask(__name__, 
	instance_path=get_instance_folder_path(), 
	instance_relative_config=True, template_folder='templates')

configure_app(app)
# Lazy initialization
cache.init_app(app)
db.init_app(app)


@app.route('/about')
def about():
    app.logger.warning('A warning message is sent.')
    app.logger.error('An error message is sent.')
    app.logger.info('Information: 3 + 2 = %d', 5)
    return "about"

# error handling

@app.errorhandler(404)
def page_not_found(error):
	app.logger.error('Page not found: %s', (request.path))
	return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', (error))
    return render_template('errors/500.html'), 500

@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', (e))
    return render_template('errors/500.html'), 500

def before_request():
    app.jinja_env.cache = {}

app.before_request(before_request)


# flask register_blueprint()

from app.main import main
from app.admin import admin

app.register_blueprint(main)
app.register_blueprint(admin, url_prefix='/admin')
