from phe_encryption import PheEncryption


conf = {
    'federated_trainer_host': 'http://localhost:8080',
    'n_iter': 2,  # can't run bigger than this due to overflow
    'eta': 1.5,
    'auto_register': True,
    'encryption': PheEncryption,
    'encryption_active': True,
    'precision': 1e-5,
}

logging_conf = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s %(module)s: %(message)s'
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
}