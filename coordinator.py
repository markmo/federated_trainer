from async_thread_pool_executor import AsyncThreadPoolExecutor
import logging
import numpy as np
import requests


class Coordinator(object):

    def __init__(self, worker_port, encryption_service, encryption_active):
        logging.debug('init with worker_port={}'.format(worker_port))
        self.worker_port = worker_port
        self.encryption_service = encryption_service
        self.encryption_active = encryption_active
        self.executor = AsyncThreadPoolExecutor()

    def send_gradient(self, workers, weights):
        logging.debug(self.send_gradient.__name__)
        args = [self._build_data(worker, weights) for worker in workers]
        self.executor.run(executable=self._send_gradient, args=args)
        # self._send_gradient(*args)

    def get_updates_from_workers(self, workers, model_type, public_key):
        logging.debug(self.get_updates_from_workers.__name__)
        args = [(worker, model_type, public_key) for worker in workers]
        results = self.executor.run(executable=self._get_update_from_worker, args=args)
        # results = self._get_update_from_worker(*args)
        # logging.info('results:\n{}'.format(results))
        return np.asarray(results)

    def get_models_from_workers(self, workers):
        logging.debug(self.get_models_from_workers.__name__)
        args = ['http://{}:{}/weights'.format(worker['host'], self.worker_port) for worker in workers]
        results = self.executor.run(executable=self._get_model_from_worker, args=args)
        # results = self._get_model_from_worker(*args)
        # logging.info('results:\n{}'.format(results))
        return np.asarray(results)

    def _build_data(self, worker, weights):
        logging.debug(self._build_data.__name__)
        return 'http://{}:{}/step'.format(worker['host'], self.worker_port), {'gradient': weights.tolist()}

    def _send_gradient(self, data):
        logging.info(self._send_gradient.__name__)
        url, payload = data
        logging.info('Calling {} [PUT] with:\n{}'.format(url, payload))
        if self.encryption_active:
            payload = {'gradient': self.encryption_service.get_serialized_collection(payload['gradient'])}

        # logging.info('Calling {} [PUT] with:\n{}'.format(url, payload))
        requests.put(url, json=payload)

    def _get_update_from_worker(self, data):
        logging.info(self._get_update_from_worker.__name__)
        # logging.info('data: {}'.format(data))
        worker, model_type, public_key = data
        url = 'http://{}:{}/weights'.format(worker['host'], self.worker_port)
        payload = {'model_type': model_type, 'public_key': public_key}
        logging.info('Calling {} [POST] with:\n{}'.format(url, payload))
        response = requests.post(url, json=payload)
        result = response.json()
        if self.encryption_active:
            result = self.encryption_service.get_deserialized_collection(result)

        logging.debug('result shape: {}'.format(np.shape(result)))
        return result

    def _get_model_from_worker(self, url):
        logging.info(self._get_model_from_worker.__name__)
        logging.info('Calling {} [GET]'.format(url))
        response = requests.get(url)
        result = response.json()
        if self.encryption_active:
            result = self.encryption_service.get_deserialized_collection(result)

        logging.debug('result shape: {}'.format(np.shape(result)))
        return result
