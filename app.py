from flask import Flask
from presentation.views import views_bp
from data import models
from data.database import engine, Base
from data.cloudinary import cloudinary_configuracion


cloudinary_configuracion()

app = Flask(__name__, template_folder='presentation/templates',
            static_folder='presentation/static')


app.register_blueprint(views_bp)

Base.metadata.create_all(bind=engine)


@app.route('/test')
def test():
    return "Hello, World!"

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True)
