from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_login import LoginManager
from flask_sock import Sock
import os

application = Flask(__name__)
application.config.from_pyfile('config.py')
sock = Sock(application)

db = SQLAlchemy(application)
bcrypt = Bcrypt(application)
api_match_start = Api(application)
login_manager = LoginManager(application)


from cargo import accounts, browse, match_status, matchpage, organiser, participants # status
from cargo.myapi import MyApiMatchStart

api_match_start.add_resource(MyApiMatchStart,
                             '/api/tour/<int:tour_id>/round/<int:round_num>/match/<int:match_num>/<string:event>')

if os.path.exists('webapp/site.db'):
    pass
else:
    db.create_all()
