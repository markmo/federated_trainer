import logging
from logging.config import dictConfig
from pathlib import Path

import numpy as np
from flask import Flask, jsonify, request

from data_loader import DataLoader
from encryption_service import EncryptionService
from model_owners.config import conf, logging_conf
from model_owners.model_owner import ModelOwner

dictConfig(logging_conf)

THIS_DIR = Path(__file__).parent


app = Flask(__name__)

encryption_service = EncryptionService(conf['encryption'])
public_key, private_key = encryption_service.generate_key_pair(conf['key_length'])
encryption_service.set_public_key(public_key.n)
encryption_active = conf['encryption_active']

data_loader = DataLoader()
data_loader.load_diabetes_data()
deployer = ModelOwner(public_key, private_key, encryption_service, data_loader, conf)


@app.route('/models', methods=['POST'])
def make_model():
    logging.info('-> ' + make_model.__name__ + ' [POST]')
    model_conf = request.get_json()
    model = deployer.make_model(model_conf)
    return jsonify(model.serialize()), 200


@app.route('/model_finished/<model_id>', methods=['PUT'])
def model_finished(model_id):
    logging.info('-> ' + model_finished.__name__ + ' [PUT]')
    params = request.get_json()
    deployer.model_finished(model_id, params)
    return jsonify('OK'), 200


@app.route('/models/<model_id>', methods=['PATCH'])
def update_model(model_id):
    logging.info('-> ' + update_model.__name__ + ' [PATCH]')
    params = request.get_json()
    params = deployer.update_model(model_id, params)
    return jsonify(params), 200


@app.route('/models', methods=['GET'])
def get_models():
    logging.info('-> ' + get_models.__name__ + ' [GET]')
    return jsonify([model.serialize() for model in deployer.models.values()])


@app.route('/models/<model_id>', methods=['GET'])
def get_model(model_id):
    logging.info('-> ' + get_model.__name__ + ' [GET]')
    return jsonify(deployer.get_model(model_id).serialize()), 200


@app.route('/prediction', methods=['GET'])
def make_prediction():
    logging.info('-> ' + make_prediction.__name__ + ' [GET]')
    data = request.get_json()
    pred = deployer.make_prediction(data)
    return jsonify(pred.serialize()), 200


@app.route('/predictions', methods=['GET'])
def get_predictions():
    logging.info('-> ' + get_predictions.__name__ + ' [GET]')
    return jsonify([pred.serialize() for pred in deployer.predictions.values()])


@app.route('/predictions/<prediction_id>', methods=['GET'])
def get_prediction(prediction_id):
    logging.info('-> ' + get_prediction.__name__ + ' [GET]')
    pred = deployer.predictions.get(prediction_id, None)
    return jsonify(pred.serialize()), 200


@app.route('/datasets', methods=['POST'])
def upload_dataset():
    logging.info('-> ' + upload_dataset.__name__ + ' [POST]')
    file = request.files.get('file')
    logging.info('Uploading file {}'.format(file.filename))
    # logging.info(file)
    file.save(THIS_DIR / 'data/data.csv')
    file.close()
    return jsonify('OK'), 200


# @app.route('/test', methods=['GET'])
# def test_model():
#     logging.info('-> ' + test_model.__name__ + ' [GET]')
#     model.fit(n_epochs=200, eta=0.1)
#     y_pred = model.predict(x_test)
#     mse = mean_squared_error(y_pred, y_test)
#     logging.info('mse: {}'.format(mse))
#     return jsonify({'pred': list(zip(y_pred.tolist(), model.y.tolist())), 'mse': mse})


@app.route('/ping', methods=['POST'])
def ping():
    logging.debug('-> ' + ping.__name__ + ' [POST]')
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
