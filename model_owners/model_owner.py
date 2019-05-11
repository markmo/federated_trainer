import logging
import uuid

import requests

from model_owners.model_container import ModelContainer
from model_owners.model_not_found_exception import ModelNotFoundException
from model_owners.model_status import ModelStatus


class ModelOwner(object):

    def __init__(self, public_key, private_key, encryption_service, data_loader, conf):
        logging.debug('init')
        self.id = str(uuid.uuid1())
        self.public_key = public_key
        self.private_key = private_key
        self.encryption_service = encryption_service
        self.data_loader = data_loader
        self.encryption_active = conf['encryption_active']
        self.registration_url = conf['registration_url']
        self.port = conf['port']
        self.models = {}
        self.predictions = {}

    def make_model(self, model_conf):
        logging.debug(self.make_model.__name__)
        model_type = model_conf['model_type']
        data_props = model_conf['data_props']
        model = ModelContainer(model_type, data_props)
        self.models[model.id] = model
        data = {
            'model_id': model.id,
            'model_type': model_type,
            'public_key': self.public_key.n,
        }
        if logging.getLogger().getEffectiveLevel() == 'DEBUG':
            logging.info('Calling {} [POST] with:\n{}'.format(self.registration_url, data))
        else:
            logging.info('Calling {} [POST]'.format(self.registration_url))

        response = requests.post(self.registration_url, json=data)
        response.raise_for_status()
        return model

    def model_finished(self, model_id, params):
        logging.debug(self.model_finished.__name__)
        self._update_model(model_id, params, ModelStatus.FINISHED)

    def update_model(self, model_id, params):
        logging.debug(self.update_model.__name__)
        model = self._update_model(model_id, params, ModelStatus.IN_PROGRESS)
        params = model.params
        if self.encryption_active:
            params = self.encryption_service.get_serialized_encrypted_collection(params)

        return params

    def _update_model(self, model_id, params, status):
        logging.debug(self._update_model.__name__)
        if self.encryption_active:
            params = self.encryption_service.decrypt_and_deserialize_collection(self.private_key, params)

        model = self.get_model(model_id)
        model.params = params
        model.status = status
        return model

    def get_model(self, model_id):
        logging.debug(self.get_model.__name__)
        return self.models.get(model_id, None)

    def make_prediction(self, data):
        logging.debug(self.make_prediction.__name__)
        model_id = data['model_id']
        model = self.get_model(model_id)
        if not model:
            raise ModelNotFoundException(model_id)

        x_test, y_test = self.data_loader.get_data()
        pred = model.predict(x_test, y_test)
        self.predictions[pred.id] = pred
        return pred

    def get_prediction(self, prediction_id):
        logging.debug(self.get_prediction.__name__)
        return self.predictions.get(prediction_id, None)
