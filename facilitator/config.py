from phe_encryption import PheEncryption


conf = {
    'n_clients': 1,
    'n_epochs': 10,
    'worker_port': 9000,
    'encryption': PheEncryption,
    'encryption_active': True,
    'model_deployer_port': 9090,
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