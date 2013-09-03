class ProductionConfig(object):
    TESTING = False
    DEBUG = True


class DebugConfig(ProductionConfig):
    TESTING = True
    DEBUG = True
