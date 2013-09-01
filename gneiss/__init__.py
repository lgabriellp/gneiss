from flask import Flask
from flask_peewee.db import Database


def App(filename):
    application = Flask(__name__)
    application.config.from_object(filename)
    return application


app = App("gneiss.config.ProductionConfig")
db = Database(app)

import gneiss.models
import gneiss.views
