import logging
from logging.config import dictConfig

from flask import Flask, jsonify, request

from encryption_service import EncryptionService
from facilitator.config import conf, logging_conf
from facilitator.federated_trainer import FederatedTrainer

dictConfig(logging_conf)


app = Flask(__name__)

encryption_service = EncryptionService(conf['encryption'])
federated_trainer = FederatedTrainer(encryption_service, conf)


@app.route('/workers', methods=['GET'])
def get_workers():
    logging.info('-> ' + get_workers.__name__ + ' [GET]')
    return jsonify([str(worker) for worker in federated_trainer.workers])


@app.route('/workers', methods=['POST'])
def register_worker():
    logging.info('-> ' + register_worker.__name__ + ' [POST]')
    data = request.get_json()
    data['host'], data['port'] = request.environ['REMOTE_ADDR'], request.environ['REMOTE_PORT']
    response = federated_trainer.register_worker(data)
    logging.info('Number workers: {}'.format(response['number']))
    return jsonify(response), 200


@app.route('/models', methods=['POST'])
def train_model():
    logging.info('-> ' + train_model.__name__ + ' [POST]')
    data = request.get_json()
    remote_addr = request.environ['REMOTE_ADDR']
    logging.info('Train model at {}:{} with:\n{}'.format(remote_addr, conf['worker_port'], data))
    federated_trainer.process(remote_addr, data)
    return jsonify('OK'), 200


@app.route('/ping', methods=['POST'])
def ping():
    logging.debug('-> ' + ping.__name__ + ' [POST]')
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
