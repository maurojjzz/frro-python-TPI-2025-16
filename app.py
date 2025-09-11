from flask import Flask
from presentation.views import views_bp

app = Flask(__name__, template_folder='presentation/templates',
            static_folder='presentation/static')


app.register_blueprint(views_bp)


@app.route('/test')
def test():
    return "Hello, World!"

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True)
