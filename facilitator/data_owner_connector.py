import logging

import numpy as np
import requests

from async_thread_pool_executor import AsyncThreadPoolExecutor


class DataOwnerConnector(object):

    def __init__(self, worker_port, encryption_service, encryption_active):
        logging.debug('init with worker_port={}'.format(worker_port))
        self.worker_port = worker_port
        self.encryption_service = encryption_service
        self.encryption_active = encryption_active
        self.executor = AsyncThreadPoolExecutor()

    def start_training_on_workers(self, workers, model_type, public_key):
        logging.debug(self.start_training_on_workers.__name__)
        args = [(worker, model_type, public_key) for worker in workers]
        results = self.executor.run(executable=self._start_training_on_worker, args=args)
        return np.asarray(results)

    def _start_training_on_worker(self, data):
        logging.info(self._start_training_on_worker.__name__)
        worker, model_type, public_key = data
        url = 'http://{}:{}/models'.format(worker['host'], self.worker_port)
        payload = {'model_type': model_type, 'public_key': public_key}
        if logging.getLogger().getEffectiveLevel() == 'DEBUG':
            logging.info('Calling {} [POST] with:\n{}'.format(url, payload))
        else:
            logging.info('Calling {} [POST]'.format(url))

        response = requests.post(url, json=payload)
        params = response.json()
        if self.encryption_active:
            params = self.encryption_service.get_deserialized_collection(params)

        logging.debug('params shape: {}'.format(np.shape(params)))
        return params

    def send_global_update(self, workers, params):
        logging.debug(self.send_global_update.__name__)
        args = [self._build_global_update_args(worker, params) for worker in workers]
        results = self.executor.run(executable=self._send_global_update, args=args)
        return np.asarray(results)

    def _build_global_update_args(self, worker, params):
        logging.debug(self._build_global_update_args.__name__)
        if self.encryption_active:
            params = self.encryption_service.get_serialized_collection(params)

        return 'http://{}:{}/params'.format(worker['host'], self.worker_port), {
            'params': params
        }

    def _send_global_update(self, data):
        logging.debug(self._send_global_update.__name__)
        url, payload = data
        if logging.getLogger().getEffectiveLevel() == 'DEBUG':
            logging.info('Calling {} [PUT] with:\n{}'.format(url, payload))
        else:
            logging.info('Calling {} [PUT]'.format(url))

        response = requests.put(url, json=payload)
        params = response.json()
        if self.encryption_active:
            params = self.encryption_service.get_deserialized_collection(params)

        logging.debug('params shape: {}'.format(np.shape(params)))
        return params

    # combine with `send_global_update`
    # def get_params_from_workers(self, workers):
    #     logging.debug(self.get_params_from_workers.__name__)
    #     args = ['http://{}:{}/params'.format(worker['host'], self.worker_port) for worker in workers]
    #     results = self.executor.run(executable=self._get_params_from_worker, args=args)
    #     return np.asarray(results)

    # def _get_params_from_worker(self, url):
    #     logging.info(self._get_params_from_worker.__name__)
    #     logging.info('Calling {} [GET]'.format(url))
    #     response = requests.get(url)
    #     params = response.json()
    #     if self.encryption_active:
    #         params = self.encryption_service.get_deserialized_collection(params)
    #
    #     logging.debug('params shape: {}'.format(np.shape(params)))
    #     return params
