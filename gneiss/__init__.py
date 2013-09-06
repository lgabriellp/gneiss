from flask import Flask


def App(filename):
    application = Flask(__name__)
    application.config.from_object(filename)

    import peewee
    import gneiss.models
    import gneiss.views

    if application.config["TESTING"]:
        database = peewee.SqliteDatabase(":memory:")
    else:
        database = peewee.SqliteDatabase("emulation.db")
    gneiss.models.proxy.initialize(database)

    application.register_blueprint(gneiss.views.stats)
    return application
