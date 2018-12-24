from datetime import timedelta

DEBUG = True
PORT = 5000
HOST = "localhost"
SECRET_KEY = "signin"

JWT_AUTH_URL_RULE = '/login'
JWT_AUTH_USERNAME_KEY = 'phonenum'
JWT_AUTH_PASSWORD_KEY = 'password'
JWT_EXPIRATION_DELTA = timedelta(seconds=600)

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'