import os

from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from celery import Celery


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:pass@localhost/sdb'
db = SQLAlchemy(app)


admin = Admin(app, name='myapp', template_mode='bootstrap3')
from models import Info
from models import Word
from models import Url
admin.add_view(ModelView(Info, db.session))
admin.add_view(ModelView(Word, db.session))
admin.add_view(ModelView(Url, db.session))


app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery_app = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery_app.conf.update(app.config)


import views


@app.cli.command('initdb')
def init_db():
    db.create_all()
