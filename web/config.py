import os


class Config:
    SERVER_NAME = os.environ.get('SERVER_NAME') or 'localhost:5000'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very hard to guess string'
    DB_ENCRYPTION_KEY = os.environ.get('DB_ENCRYPTION_KEY') or 'very hard to guess string'

    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BYTARDAG_ADMIN = os.environ.get('BYTARDAG_ADMIN')

    BYTARDAG_MAIL_SENDER_ADDRESS = os.environ.get('MAIL_SENDER') or 'info@bytardag.se'
    BYTARDAG_MAIL_SENDER_NAME = os.environ.get('MAIL_SENDER') or 'Eksjö Klädbytardag'
    BYTARDAG_MAIL_REPLY_TO = os.environ.get('MAIL_REPLY_TO') or 'Eksjö Klädbytardag <info@bytardag.se>'
    BYTARDAG_MAIL_SUBJECT_PREFIX = os.environ.get('MAIL_SUBJECT_PREFIX') or '[bytardag.se]'

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or '127.0.0.1'
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_PORT = os.environ.get('MAIL_PORT') or 587
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    SENDGRID_APIKEY = os.environ.get('SENDGRID_APIKEY')
    SENDGRID_APIURL = os.environ.get('SENDGRID_APIURL') or 'https://api.sendgrid.com/v3/'

    SENDGRID_WEBHOOK_USERNAME = os.environ.get('SENDGRID_WEBHOOK_USERNAME') or 'sendgrid'
    SENDGRID_WEBHOOK_PASSWORD = os.environ.get('SENDGRID_WEBHOOK_PASSWORD') or 'secretpassword'

    # Celery: Broker settings

    RABBITMQ_HOSTNAME = os.getenv('RABBITMQ_PORT_5672_TCP') or 'rabbitmq:5672'

    if RABBITMQ_HOSTNAME.startswith('tcp://'):
        RABBITMQ_HOSTNAME = RABBITMQ_HOSTNAME.split('//')[1]

    BROKER_URL = os.getenv('BROKER_URL') or 'amqp://{user}:{password}@{hostname}/{vhost}/'.format(
        user=os.getenv('RABBITMQ_DEFAULT_USER') or 'rabbitmq',
        password=os.getenv('RABBITMQ_DEFAULT_PASSWORD') or 'secretpassword',
        hostname=RABBITMQ_HOSTNAME,
        vhost=os.getenv('RABBITMQ_ENV_VHOST') or '')

#    BROKER_HEARTBEAT = '?heartbeat=30'
#    if not BROKER_URL.endswith(BROKER_HEARTBEAT):
#        BROKER_URL += BROKER_HEARTBEAT

    BROKER_POOL_LIMIT = 1
    BROKER_CONNECTION_TIMEOUT = 10

    # Celery: Result backend settings

    CELERY_RESULT_BACKEND = os.getenv('RESULT_BACKEND') or 'redis://{hostname}:{port}/{db}'.format(
        hostname=os.getenv('REDIS_PORT_6379_TCP_ADDR') or 'redis',
        port=6379,
        db=0)

    # Celery: Basic settings

    CELERY_ENABLE_UTC = True
    CELERY_TIMEZONE = 'UTC'

    CELERY_ALWAYS_EAGER = False
    CELERY_ACKS_LATE = True
    CELERY_TASK_PUBLISH_RETRY = True
    CELERY_DISABLE_RATE_LIMITS = False

    CELERY_TASK_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_RESULT_SERIALIZER = 'json'

    CELERYD_HIJACK_ROOT_LOGGER = False
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERYD_MAX_TASKS_PER_CHILD = 1000

    # List with all the modules containing tasks for celery

    CELERY_IMPORTS = ['app.email']

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or \
        'postgresql+psycopg2://postgres:secretpassword@postgresql/development'

    MAIL_SUPPRESS_SEND = True

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        app.logger.setLevel(logging.DEBUG)


class TestingConfig(Config):
    TESTING = True

    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or \
        'postgresql+psycopg2://postgres:secretpassword@postgresql/testing'

    WTF_CSRF_ENABLED = False

    CELERY_ALWAYS_EAGER = True

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        app.testing = True

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'postgresql+psycopg2://postgres:secretpassword@localhost/bytardag'

    PREFERRED_URL_SCHEME = 'https'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from app.logging import SendGridHandler
        mail_handler = SendGridHandler(cls.SENDGRID_APIKEY,
                                       cls.BYTARDAG_ADMIN,
                                       'logger@bytardag.se')
        mail_handler.setFormatter(logging.Formatter('''
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
'''))
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class StagingConfig(ProductionConfig):
    STAGING = True

    PREFERRED_URL_SCHEME = 'https'

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)


class CeleryConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('CELERY_DATABASE_URI') or \
        'postgresql+psycopg2://postgres:secretpassword@postgresql/development'

    PREFERRED_URL_SCHEME = 'https'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'celery': CeleryConfig,

    'default': DevelopmentConfig
}
