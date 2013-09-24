import peewee
from flask import Flask


def App(filename="gneiss.config.ProductionConfig"):
    app = Flask(__name__)
    app.config.from_object(filename)

    import gneiss.models
    import gneiss.views

    database = peewee.SqliteDatabase(app.config["DATABASE_URL"])
    gneiss.models.proxy.initialize(database)

    app.register_blueprint(gneiss.views.stats)
    return app
