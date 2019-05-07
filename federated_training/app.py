from encryption_service import EncryptionService
from federated_trainer import FederatedTrainer
from federated_training.config import conf
from flask import Flask, jsonify, request
import logging
from logging.config import dictConfig

dictConfig({
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
})


app = Flask(__name__)

encryption_service = EncryptionService(conf['encryption'])
federated_trainer = FederatedTrainer(encryption_service, conf)


@app.route('/workers', methods=['GET'])
def get_workers():
    logging.debug(get_workers.__name__ + ' [GET]')
    return jsonify([str(worker) for worker in federated_trainer.workers])


@app.route('/workers', methods=['POST'])
def register_worker():
    logging.debug(register_worker.__name__ + ' [POST]')
    data = request.get_json()
    data['host'], data['port'] = request.environ['REMOTE_ADDR'], request.environ['REMOTE_PORT']
    response = federated_trainer.register_worker(data)
    logging.info('Number workers: {}'.format(response['number']))
    return jsonify(response), 200


@app.route('/models', methods=['POST'])
def train_model():
    logging.debug(train_model.__name__ + ' [POST]')
    data = request.get_json()
    remote_addr = request.environ['REMOTE_ADDR']
    logging.info('Train model at {} with:\n{}'.format(remote_addr, data))
    federated_trainer.process(remote_addr, data)
    return jsonify('OK'), 200


@app.route('/ping', methods=['POST'])
def ping():
    logging.debug(ping.__name__ + ' [POST]')
    return jsonify('pong'), 200


# @app.errorhandler(Exception)
def _handle_error(error):
    class_name = error.__class__.__name__
    message = [str(x) for x in error.args]
    logging.error('Error in {}: {}'.format(class_name, message))
    status_code = int(error.status_code) if hasattr(error, 'status_code') else 500
    response = {
        'success': False,
        'error': {
            'type': class_name,
            'message': message
        }
    }
    return jsonify(response), status_code
