from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_login import LoginManager
import os

application = Flask(__name__)
application.config['SECRET_KEY'] = 'akjdb9qfucq80eb039ru348024830294whfipsdkl'
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
application.config['SERVER_URL'] = 'http://freddyhome.ddns.net'
application.config['STEAM_API_KEY'] = '8C75B9586976DFCAF894BD72AAC00538'
db = SQLAlchemy(application)
bcrypt = Bcrypt(application)
api_match_start = Api(application)
# sock = SocketIO(application, cors_allowed_origins='*')
login_manager = LoginManager(application)


from cargo import routes, status
# from cargo.myapi import MyApiMatchStart

# api_match_start.add_resource(MyApiMatchStart, '/api/match/<string:match_id>/<string:event>')

if os.path.exists('webapp/site.db'):
    pass
else:
    db.create_all()
