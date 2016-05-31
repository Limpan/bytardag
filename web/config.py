import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very hard to guess string'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BYTARDAG_ADMIN = os.environ.get('BYTARDAG_ADMIN')

    BYTARDAG_MAIL_SENDER = 'Eksjö Klädbytardag <info@bytardag.se>'
    BYTARDAG_MAIL_SUBJECT_PREFIX = '[bytardag.se]'

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or '127.0.0.1'
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_PORT = os.environ.get('MAIL_PORT') or 587
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

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

    CELERY_IMPORTS = ['app.email.tasks']

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or \
        'postgresql+psycopg2://postgres:secretpassword@localhost/development'


class TestingConfig(Config):
    TESTING = True

    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or \
        'postgresql+psycopg2://postgres:secretpassword@localhost/testing'

    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'postgresql+psycopg2://postgres:secretpassword@localhost/bytardag'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
                                   fromaddr=cls.BYTARDAG_MAIL_SENDER,
                                   toaddrs=[cls.BYTARDAG_ADMIN],
                                   subject=cls.BYTARDAG_MAIL_SUBJECT_PREFIX + ' Application Error',
                                   credentials=credentials,
                                   secure=secure)
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


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        import logging
        from logging.handlers import StreamHandler
        stream_handler = StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)


class CeleryConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('CELERY_DATABASE_URI') or \
        'postgresql+psycopg2://postgres:secretpassword@postgresql/development'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'celery': CeleryConfig,

    'default': DevelopmentConfig
}
