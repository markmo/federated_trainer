import logging
from logging.config import dictConfig
from pathlib import Path

from flask import Flask, jsonify, request

from data_loader import DataLoader
from data_owners.config import conf, logging_conf
from data_owners.worker import Worker
from encryption_service import EncryptionService

dictConfig(logging_conf)

THIS_DIR = Path(__file__).parent


app = Flask(__name__)

encryption_service = EncryptionService(conf['encryption'])
encryption_active = conf['encryption_active']

data_loader = DataLoader()
data_loader.load_data()
worker = Worker(conf, data_loader, encryption_service)


@app.route('/datasets', methods=['POST'])
def upload_data():
    logging.debug('-> ' + upload_data.__name__ + ' [POST]')
    file = request.files.get('file')
    logging.info('Uploading file {}'.format(file.filename))
    # logging.info(file)
    file.save(THIS_DIR / 'data/data.csv')
    file.close()
    return jsonify('OK'), 200


@app.route('/models', methods=['POST'])
def train_model():
    logging.info('-> ' + train_model.__name__ + ' [POST]')
    data = request.get_json()
    params = worker.train(data['model_type'], data['public_key'])
    if encryption_active:
        params = encryption_service.get_serialized_encrypted_collection(params, conf['precision'])

    return jsonify(params), 200


@app.route('/params', methods=['PUT'])
def update_model():
    logging.info('-> ' + update_model.__name__ + ' [PUT]')
    updates = request.get_json()['params']
    if encryption_active:
        updates = encryption_service.get_deserialized_collection(updates)

    params = worker.step(updates)
    if encryption_active:
        params = encryption_service.get_serialized_encrypted_collection(params, conf['precision'])

    return jsonify(params), 200


# @app.route('/params', methods=['GET'])
# def get_params():
#     logging.info('-> ' + get_params.__name__ + ' [GET]')
#     params = worker.get_params_list()
#     if encryption_active:
#         params = encryption_service.get_serialized_collection(params)
#
#     return jsonify(params), 200


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
