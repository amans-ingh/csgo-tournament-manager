import importlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_login import LoginManager
from flask_sock import Sock
from flask_apscheduler import APScheduler
from sqlalchemy import create_engine

application = Flask(__name__)
application.config.from_pyfile('config.py')
sock = Sock(application)
scheduler = APScheduler()
scheduler.init_app(application)
scheduler.start()
db = SQLAlchemy(application)
bcrypt = Bcrypt(application)
api_match_start = Api(application)
login_manager = LoginManager(application)


from cargo import accounts, browse, match_status, matchpage, organiser, participants
from cargo.myapi import MyApiMatchStart
from cargo.models import Tournament, Team, Match, MapStats, User, Registration, Servers, PlayerStats, Rounds

api_match_start.add_resource(MyApiMatchStart,
                             '/api/tour/<int:tour_id>/round/<int:round_num>/match/<int:match_num>/<string:event>')

engine = create_engine(application.config['SQLALCHEMY_DATABASE_URI'])
connection = engine.connect()
table_models = importlib.import_module('cargo.models')
if not engine.dialect.has_table(connection, "User"):
    ORMTable = getattr(table_models, "User")
    ORMTable.__table__.create(bind=engine, checkfirst=True)

if not engine.dialect.has_table(connection, "Tournament"):
    ORMTable = getattr(table_models, "Tournament")
    ORMTable.__table__.create(bind=engine, checkfirst=True)

if not engine.dialect.has_table(connection, "Team"):
    ORMTable = getattr(table_models, "Team")
    ORMTable.__table__.create(bind=engine, checkfirst=True)

if not engine.dialect.has_table(connection, "Match"):
    ORMTable = getattr(table_models, "Match")
    ORMTable.__table__.create(bind=engine, checkfirst=True)

if not engine.dialect.has_table(connection, "MapStats"):
    ORMTable = getattr(table_models, "MapStats")
    ORMTable.__table__.create(bind=engine, checkfirst=True)

if not engine.dialect.has_table(connection, "Registration"):
    ORMTable = getattr(table_models, "Registration")
    ORMTable.__table__.create(bind=engine, checkfirst=True)

if not engine.dialect.has_table(connection, "Servers"):
    ORMTable = getattr(table_models, "Servers")
    ORMTable.__table__.create(bind=engine, checkfirst=True)

if not engine.dialect.has_table(connection, "PlayerStats"):
    ORMTable = getattr(table_models, "PlayerStats")
    ORMTable.__table__.create(bind=engine, checkfirst=True)

if not engine.dialect.has_table(connection, "Rounds"):
    ORMTable = getattr(table_models, "Rounds")
    ORMTable.__table__.create(bind=engine, checkfirst=True)
