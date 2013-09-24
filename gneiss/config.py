class Production(object):
    TESTING = False
    DEBUG = False
    DATABASE_URL = "emulation.db"


class Testing(object):
    TESTING = True
    DEBUG = True
    CREATE_SCHEMA = True
    DATABASE_URL = ":memory:"


class PersistentTesting(Testing):
    CREATE_SCHEMA = False
    DATABASE_URL = "emulation.db"
