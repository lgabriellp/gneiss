class ProductionConfig(object):
    DATABASE = {
        "name": "emulation.db",
        "engine": "peewee.SqliteDatabase"
    }

    TESTING = False
    DEBUG = False


class DebugConfig(ProductionConfig):
    DATABASE = {
        "name": ":memory:",
        "engine": "peewee.SqliteDatabase"
    }

    TESTING = True
    DEBUG = True
