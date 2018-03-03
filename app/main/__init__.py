from flask import Blueprint
from app.data.models import Permission


main = Blueprint('main', __name__, template_folder='templates')

from . import views

@main.app_context_processor
def inject_permissions():
	return dict(Permission=Permission)