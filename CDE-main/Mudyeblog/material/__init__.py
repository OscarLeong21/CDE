from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = '451002d5999c0e9cd687a4c0a1f92e5c'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://oscar:205CDE@localhost/dbflask'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from material import routes
