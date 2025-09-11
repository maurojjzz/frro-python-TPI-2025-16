from flask import Blueprint, render_template, jsonify

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    return "Este es el index, wachin"

@views_bp.route('/hello/<name>')
def hello(name):
    return f"Hello {name}! tremendo loro"
