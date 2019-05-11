import logging
import uuid

import numpy as np

from data_owners.facilitator_connector import FacilitatorConnector
from model_factory import ModelFactory


class Worker(object):

    def __init__(self, conf, data_loader, encryption_service):
        logging.info('init with:\n{}'.format(conf))
        self.worker_id = str(uuid.uuid1())
        self.worker_name = 'Worker {}'.format(self.worker_id)
        self.conf = conf
        self.data_loader = data_loader
        self.encryption_service = encryption_service
        self.n_iter = int(conf['n_iter'])
        self.eta = float(conf['eta'])
        self.registration_number = None
        self.model = None
        if conf['auto_register']:
            self.register()

    def register(self):
        logging.debug(self.register.__name__)
        data = {'id': self.worker_id}
        response = FacilitatorConnector(self.conf).register(data)
        self.registration_number = int(response['number']) - 1

    def train(self, model_type, public_key=None):
        logging.debug(self.train.__name__)
        if public_key is not None:
            self.encryption_service.set_public_key(public_key)

        if self.model is None:
            x, y = self.data_loader.get_data()
            logging.debug('x shape: {}'.format(x.shape))
            self.model = ModelFactory.get_model(model_type)(x, y)

        params = self.model.fit(self.n_iter, self.eta)
        logging.debug('params shape: {}'.format(params.shape))
        return params.tolist()

    def step(self, params):
        logging.debug(self.step.__name__)
        params = np.asarray(params)
        logging.debug('params shape: {}'.format(params.shape))
        self.model.params = params
        params = self.model.fit(self.n_iter, self.eta)
        return params.tolist()

    def get_params_list(self):
        logging.debug(self.get_params_list.__name__)
        return self.model.params.tolist()
