DEBUG = True
PORT = 5000
HOST = "localhost"
SECRET_KEY = "signin"

JWT_AUTH_URL_RULE = '/login'
JWT_AUTH_USERNAME_KEY = 'phonenum'
JWT_AUTH_PASSWORD_KEY = 'password'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'