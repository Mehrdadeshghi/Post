from flask import Blueprint

management_bp = Blueprint('management', __name__)

from . import routes
