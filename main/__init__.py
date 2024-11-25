from flask import Flask
import stripe
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.contrib.google import make_google_blueprint

csrf = CSRFProtect()
mail = Mail()

def create_app():
    from main.models import db
    app = Flask(__name__, static_folder='static')
    app.config.from_pyfile("config.py", silent=True)
    app.config['JSON_AS_ASCII'] = False

    # Set the Stripe API key
    stripe.api_key = app.config['STRIPE_SECRET_KEY']

    db.init_app(app)
    migrate = Migrate(app, db)
    socketio = SocketIO(app)
    csrf.init_app(app)
    mail.init_app(app)
    Bootstrap(app)

    # OAuth client initialization
    facebook_bp = make_facebook_blueprint(
        client_id=app.config['FACEBOOK_OAUTH_CLIENT_ID'],
        client_secret=app.config['FACEBOOK_OAUTH_CLIENT_SECRET'],
        redirect_to='connect_facebook'
    )
    google_bp = make_google_blueprint(
        client_id=app.config['GOOGLE_OAUTH_CLIENT_ID'],
        client_secret=app.config['GOOGLE_OAUTH_CLIENT_SECRET'],
        redirect_to='connect_google',
        scope=['profile', 'email']
    )

    # Register blueprints
    app.register_blueprint(facebook_bp, url_prefix='/facebook_login')
    app.register_blueprint(google_bp, url_prefix='/google_login')

    return app, socketio


app, socketio = create_app()

from main import user_routes, admin_routes
from main.forms import *
