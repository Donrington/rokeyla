from sqlalchemy import create_engine
import psycopg2
import stripe
from os import getenv

# user = getenv('AMANIGO_USER')
# password = getenv('AMANIGO_PWD')
# database = getenv('AMANIGO_DB')
# host = getenv('AMANIGO_HOST')


config = {
    'user': 'rokeyla_user',
    'password': 'nU6gniCxu66hIvptwYHj4G4WMoWLaMmJ',
    'host': 'dpg-ct2gbud6l47c73c92p3g-a.oregon-postgres.render.com',
    'database': 'rokeyla'
}

# Connect to PostgreSQL using psycopg2
connection = psycopg2.connect(
    user=config['user'],
    password=config['password'],
    host=config['host'],
    database=config['database']
)


SECRET_KEY = "THTD673&?/YHG/@H393_YEU"
ADMIN_EMAIL = "admin@personal.com"
USER_PROFILE_PATH = "main/static/uploads/"
ADMIN_PROFILE_PATH = "main/static/uploads/admins"
PRODUCT_UPLOADER = "main/static/products/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
# SQLALCHEMY_DATABASE_URI=f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
# SQLALCHEMY_DATABASE_URI="mysql+mysqlconnector://root@127.0.0.1/rokeyla"

SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://rokeyla_user:nU6gniCxu66hIvptwYHj4G4WMoWLaMmJ@dpg-ct2gbud6l47c73c92p3g-a.oregon-postgres.render.com/rokeyla"

STRIPE_PUBLISHABLE_KEY = 'your_publishable_key'
STRIPE_SECRET_KEY = 'your_secret_key'


MAIL_SERVER='smtp.gmail.com'
MAIL_PORT=465
MAIL_USERNAME='carryoby@gmail.com'
MAIL_PASSWORD='pzvw jfdf swwa lmcw'
MAIL_USE_SSL=True


FACEBOOK_OAUTH_CLIENT_ID = "YOUR_FACEBOOK_CLIENT_ID"
FACEBOOK_OAUTH_CLIENT_SECRET = "YOUR_FACEBOOK_CLIENT_SECRET"
GOOGLE_OAUTH_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"
GOOGLE_OAUTH_CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET"

