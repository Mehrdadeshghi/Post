from flask import Blueprint

management_bp = Blueprint('management', __name__)

from management import routes
