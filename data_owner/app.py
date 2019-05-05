from data_loader import DataLoader
from data_owner.config import conf
from encryption_service import EncryptionService
from flask import Flask, jsonify, request
import logging
from logging.config import dictConfig
from pathlib import Path
from worker import Worker

THIS_DIR = Path(__file__).parent

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
encryption_active = conf['encryption_active']

data_loader = DataLoader()
data_loader.load_data()
worker = Worker(conf, data_loader, encryption_service)


@app.route('/datasets', methods=['POST'])
def upload_data():
    logging.info(upload_data.__name__)
    file = request.files.get('file')
    logging.info('Uploading file {}'.format(file.filename))
    logging.info(file)
    file.save(THIS_DIR / 'data/data.csv')
    file.close()
    return jsonify('OK'), 200


@app.route('/weights', methods=['GET'])
def get_weights():
    logging.info(get_weights.__name__)
    result = worker.get_weights()
    if encryption_active:
        result = encryption_service.get_serialized_collection(result)

    return jsonify(result), 200


@app.route('/weights', methods=['POST'])
def process_weights():
    logging.info(process_weights.__name__)
    data = request.get_json()
    model_type = data['model_type']
    public_key = data['public_key']
    result = worker.process(model_type, public_key)
    if encryption_active:
        result = encryption_service.get_serialized_encrypted_collection(result)

    return jsonify(result), 200


@app.route('/step', methods=['PUT'])
def gradient_step():
    logging.info(gradient_step.__name__)
    data = request.get_json()['gradient']
    if encryption_active:
        data = encryption_service.get_deserialized_collection(data)

    worker.step(data)
    return jsonify('OK'), 200


@app.route('/ping', methods=['POST'])
def ping():
    logging.info(ping.__name__)
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
