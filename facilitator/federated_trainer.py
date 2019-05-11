import logging
from functools import reduce
from threading import Thread

import numpy as np

from facilitator.data_owner_connector import DataOwnerConnector
from facilitator.model_owner_connector import ModelOwnerConnector


class FederatedTrainer(object):

    def __init__(self, encryption_service, conf):
        logging.debug('init with:\n{}'.format(conf))
        self.encryption_service = encryption_service
        self.conf = conf
        self.encryption_active = conf['encryption_active']
        self.workers = []
        self.data_owner_connector = DataOwnerConnector(conf['worker_port'], encryption_service,
                                                       encryption_active=self.encryption_active)
        self.model_deployer_connector = ModelOwnerConnector(conf['model_deployer_port'])

    def register_worker(self, worker):
        logging.info(self.register_worker.__name__)
        logging.info(worker)
        self.workers.append(worker)
        return {'number': len(self.workers)}

    def process(self, remote_addr, data):
        logging.debug(self.process.__name__)
        self.model_deployer_connector.remote_addr = remote_addr
        self.model_deployer_connector.model_id = data['model_id']
        args = (self._federated_learning, data['model_type'], data['public_key'])
        logging.debug('args: {}'.format(args))
        Thread(target=self._async_server_processing, args=args).start()

    def _async_server_processing(self, func, *args):
        logging.debug(self._async_server_processing.__name__)
        params = func(*args)
        if self.encryption_active:
            params = self.encryption_service.get_serialized_collection(params)

        self.model_deployer_connector.send_model_finished(params)

    def _federated_learning(self, model_type, public_key):
        logging.info(self._federated_learning.__name__)
        self.encryption_service.set_public_key(public_key)
        params = self._start_training(model_type, public_key)
        logging.debug('params shape: {}'.format(params.shape))
        params = self._federated_average(params)
        logging.debug('federated_averaging shape: {}'.format(params.shape))
        for i in range(self.conf['n_epochs']):
            logging.info('Epoch {}'.format(i + 1))
            params = self._send_global_update(params)

            # combine with update above
            # params = self._get_trained_models()
            # logging.debug('params shape: {}'.format(params.shape))

            params = self._federated_average(params)
            if self.encryption_active:
                updates = self.encryption_service.get_serialized_collection(params)
            else:
                updates = params

            params = self.model_deployer_connector.send_model_update(updates)
            if self.encryption_active:
                params = np.asarray(self.encryption_service.get_deserialized_collection(params))

        logging.debug('federated_averaging final shape: {}'.format(params.shape))
        return params

    def _start_training(self, model_type, public_key) -> np.ndarray:
        logging.debug(self._start_training.__name__)
        return self.data_owner_connector.start_training_on_workers(self.workers, model_type, public_key)

    def _send_global_update(self, params):
        logging.debug(self._send_global_update.__name__)
        return self.data_owner_connector.send_global_update(self.workers, params)

    def _federated_average(self, updates: np.ndarray) -> np.ndarray:
        logging.debug(self._federated_average.__name__)
        if len(updates) == 1:
            return updates[0]

        return reduce(sum_collection, updates) / len(self.workers)

    # def _get_trained_models(self):
    #     logging.debug(self._get_trained_models.__name__)
    #     return self.data_owner_connector.get_params_from_workers(self.workers)


def sum_collection(x, y):
    # if len(x) != len(y):
    #     raise ValueError('Vectors must be the same size')

    return x + y
