from flask import Flask

import peewee
from playhouse.proxy import Proxy

proxy = Proxy()


def App(filename):
    application = Flask(__name__)
    application.config.from_object(filename)

    import gneiss.models
    import gneiss.views

    if application.config["TESTING"]:
        database = peewee.SqliteDatabase(":memory:")
    else:
        database = peewee.SqliteDatabase("emulation.db")
    proxy.initialize(database)

    application.register_blueprint(gneiss.views.stats)
    return application


app = App("gneiss.config.ProductionConfig")
