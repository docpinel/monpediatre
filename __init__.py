from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    from .routes import routes  # Assurez-vous que votre app.py est nommé routes.py ou ajustez le chemin en conséquence
    app.register_blueprint(routes)
    
    return app