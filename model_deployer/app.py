from data_loader import DataLoader
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

x_train, y_train, x_test, y_test = DataLoader().load_diabetes_data()
model = ModelFactory.get_model(ModelType.LINEAR_REGRESSION.name)(x_train, y_train)
logging.info('x_train shape: {}'.format(x_train.shape))


@app.route('/finished', methods=['POST'])
def finished():
    logging.info(finished.__name__)
    weights = request.get_json()
    model.set_weights(weights)
    return jsonify(weights), 200


@app.route('/model', methods=['POST'])
def make_model():
    logging.info(make_model.__name__)
    registration_url = conf['server_registration_url']
    args = {
        'model_type': ModelType.LINEAR_REGRESSION.name,
        'cb_endpoint': 'finished',
        'cb_port': conf['port'],
    }
    logging.info('Calling {} with:\n{}'.format(registration_url, args))
    response = requests.post(registration_url, json=args)
    response.raise_for_status()
    return jsonify('OK'), 200


@app.route('/prediction', methods=['GET'])
def get_prediction():
    logging.info(get_prediction.__name__)
    y_pred = model.predict(x_test)
    loss = mse(y_pred, y_test)
    logging.info('mse {}'.format(loss))
    return jsonify({'pred': y_pred.tolist(), 'loss': loss})


@app.route('/ping', methods=['POST'])
def ping():
    logging.info(ping.__name__)
    return jsonify('pong'), 200


def mse(y_pred, y):
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
