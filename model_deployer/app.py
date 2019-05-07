from data_loader import DataLoader
from encryption_service import EncryptionService
from flask import Flask, jsonify, request
import logging
from logging.config import dictConfig
from model_factory import ModelFactory, ModelType
from model_deployer.config import conf
import numpy as np
import requests

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
public_key, private_key = encryption_service.generate_key_pair(conf['key_length'])
encryption_service.set_public_key(public_key.n)
encryption_active = conf['encryption_active']

x_train, y_train, x_test, y_test = DataLoader().load_diabetes_data()
model = ModelFactory.get_model(ModelType.LINEAR_REGRESSION.name)(x_train, y_train)
logging.debug('x_train shape: {}'.format(x_train.shape))


@app.route('/finished', methods=['POST'])
def finished():
    logging.info(finished.__name__ + ' [POST]')
    weights = request.get_json()
    if encryption_active:
        weights = encryption_service.decrypt_and_deserialize_collection(private_key, weights)

    model.set_weights(weights)
    return jsonify(weights), 200


@app.route('/model', methods=['POST'])
def make_model():
    logging.debug(make_model.__name__ + ' [POST]')
    registration_url = conf['server_registration_url']
    payload = {
        'model_type': ModelType.LINEAR_REGRESSION.name,
        'cb_endpoint': 'finished',
        'cb_port': conf['port'],
        'public_key': public_key.n,
    }
    logging.info('Calling {} [POST] with:\n{}'.format(registration_url, payload))
    response = requests.post(registration_url, json=payload)
    response.raise_for_status()
    return jsonify('OK'), 200


@app.route('/prediction', methods=['GET'])
def get_prediction():
    logging.info(get_prediction.__name__ + ' [GET]')
    y_pred = model.predict(x_test)
    mse = mean_squared_error(y_pred, y_test)
    logging.info('mse: {}'.format(mse))
    return jsonify({'pred': list(zip(y_pred.tolist(), model.y.tolist())), 'mse': mse})


@app.route('/test', methods=['GET'])
def test_model():
    logging.info(test_model.__name__ + ' [GET]')
    model.fit(n_epochs=200, eta=0.1)
    y_pred = model.predict(x_test)
    mse = mean_squared_error(y_pred, y_test)
    logging.info('mse: {}'.format(mse))
    return jsonify({'pred': list(zip(y_pred.tolist(), model.y.tolist())), 'mse': mse})


@app.route('/ping', methods=['POST'])
def ping():
    logging.debug(ping.__name__ + ' [POST]')
    return jsonify('pong'), 200


def mean_squared_error(y_pred, y):
    """ :math:`1/m * \\sum_{i=1..m} (y_pred_i - y_i)^2` """
    return np.mean((y - y_pred) ** 2)


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
