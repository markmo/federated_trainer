from federated_trainer_connector import FederatedTrainerConnector
import logging
from model_factory import ModelFactory
import numpy as np
import uuid


class Worker(object):

    def __init__(self, conf, data_loader, encryption_service):
        logging.info('init with:\n{}'.format(conf))
        self.worker_id = str(uuid.uuid1())
        self.worker_name = 'Worker {}'.format(self.worker_id)
        self.conf = conf
        self.data_loader = data_loader
        self.encryption_service = encryption_service
        self.registration_number = None
        self.model = None
        if conf['registration_enabled']:
            self.register()

    def process(self, model_type, public_key):
        logging.info(self.process.__name__)
        self.encryption_service.set_public_key(public_key)
        x, y = self.data_loader.get_data()
        logging.info('x shape: {}'.format(x.shape))
        self.model = self.model if self.model else ModelFactory.get_model(model_type)(x, y)
        # logging.info('model: {}'.format(self.model))
        grad = self.model.compute_gradient()
        logging.info('grad shape: {}'.format(grad.shape))
        return grad.tolist()

    def register(self):
        logging.info(self.register.__name__)
        data = {'id': self.worker_id}
        response = FederatedTrainerConnector(self.conf).register(data)
        self.registration_number = int(response['number']) - 1

    def step(self, weights):
        logging.info(self.step.__name__)
        self.model.gradient_step(np.asarray(weights), float(self.conf['eta']))

    def get_registration_number(self):
        logging.info(self.get_registration_number.__name__)
        return self.registration_number

    def get_weights(self):
        logging.info(self.get_weights.__name__)
        return self.model.weights.tolist()
