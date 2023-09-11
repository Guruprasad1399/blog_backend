from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:4200"])
    app.config.from_object(Config)

    # Configure JWT
    app.config['JWT_SECRET_KEY'] = 'DgttbneSKlcalVLdLMTxjnRdQ07ZTcUX'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 36000 # 10 hours in seconds

    jwt = JWTManager(app)
    db.init_app(app)
    
    # Initialize Migrate
    migrate = Migrate(app, db)  # This is the integration step for Flask-Migrate

    from .routes import main
    app.register_blueprint(main)

    return app
