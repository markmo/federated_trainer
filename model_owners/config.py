from phe_encryption import PheEncryption


conf = {
    'registration_url': 'http://localhost:8080/models',
    'port': 9090,
    'encryption': PheEncryption,
    'key_length': 4096,  # necessary to avoid overflow (vs. default 1024), but really slow
    'encryption_active': True,
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