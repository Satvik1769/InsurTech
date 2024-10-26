from flask import Flask
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from .routes.user_routes import user_bp
from .routes.auth_routes import auth_bp
from .routes.policy_routes import policy_bp

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.debug = True 
    bcrypt = Bcrypt(app)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(policy_bp, url_prefix='/policy')

    

    app.config['bcrypt'] = bcrypt


    return app
