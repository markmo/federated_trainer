import logging
import uuid

import numpy as np

from model_owners.model_status import ModelStatus
from model_factory import ModelFactory


class ModelContainer(object):

    def __init__(self, model_type, data_props):
        logging.debug('init')
        self.id = str(uuid.uuid1())
        self.model_type = model_type
        self.data_props = data_props
        self.model = ModelFactory.get_model(model_type)()
        self.status = ModelStatus.INITIATED

    @property
    def params(self):
        logging.debug('get_params')
        return self.model.params

    @params.setter
    def params(self, params):
        logging.debug('set_params')
        self.model.params = params

    def predict(self, x, y):
        logging.debug(self.predict.__name__)
        x = np.asarray(x)
        y = np.asarray(y)
        return self.model.predict(x, y)

    def serialize(self):
        return {
            'id': self.id,
            'status': self.status.name,
            'model_type': self.model_type,
            'data_props': self.data_props,
            'params': self.params,
        }
