from flask import Blueprint, render_template, jsonify

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    return render_template('index.html')

@views_bp.route('/hello/<name>')
def hello(name):
    return f"Hello {name}!"
