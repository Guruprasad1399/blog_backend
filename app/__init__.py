import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from flask_uploads import UploadSet, configure_uploads, IMAGES

db = SQLAlchemy()
photos = UploadSet('photos', IMAGES)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=["http://localhost:4200"])

    db.init_app(app)
    migrate = Migrate(app, db)  # This is the integration step for Flask-Migrate

    # Configure JWT
    app.config['JWT_SECRET_KEY'] = 'DgttbneSKlcalVLdLMTxjnRdQ07ZTcUX'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 36000 # 10 hours in seconds
    jwt = JWTManager(app)

    # Image Uploads
    app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../images')
    configure_uploads(app, photos)

    from .routes import main
    app.register_blueprint(main)

    return app