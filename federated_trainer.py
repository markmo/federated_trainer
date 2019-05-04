from coordinator import Coordinator
from functools import reduce
import logging
import requests
from threading import Thread


class FederatedTrainer(object):

    def __init__(self, conf):
        logging.info('init with:\n{}'.format(conf))
        self.conf = conf
        self.workers = []
        self.coordinator = Coordinator(conf['worker_port'])

    def register_worker(self, worker):
        logging.info(self.register_worker.__name__)
        self.workers.append(worker)
        return {'number': len(self.workers)}

    def process(self, remote_addr, data):
        logging.info(self.process.__name__)
        args = self._build_args(remote_addr, data)
        logging.info('args: {}'.format(args))
        # self._async_server_processing(*args)
        Thread(target=self._async_server_processing, args=args).start()

    def _async_server_processing(self, remote_addr, cb_endpoint, cb_port, func, *args):
        logging.info(self._async_server_processing.__name__)
        remote_host = 'http://{}:{}'.format(remote_addr, cb_port)
        cb_url = '{}/{}'.format(remote_host, cb_endpoint)
        result = func(*args)
        logging.info('Calling {}'.format(cb_url))
        requests.post(cb_url, json=result)

    def _build_args(self, remote_addr, data):
        logging.info(self._build_args.__name__)
        return (remote_addr,
                data['cb_endpoint'],
                data['cb_port'],
                self._federated_learning_wrapper,
                data['model_type'],
                '')

    def _federated_learning_wrapper(self, model_type, public_key):
        logging.info(self._federated_learning_wrapper.__name__)
        return self._federated_learning(model_type, public_key)

    def _federated_learning(self, model_type, public_key):
        logging.info(self._federated_learning.__name__)
        models = []
        for i in range(self.conf['n_epochs']):
            updates = self._get_updates(model_type, public_key)
            updates = self._federated_averaging(updates)
            self._send_global_model(updates)
            models = self._get_trained_models()

        return self._federated_averaging(models)

    def _get_updates(self, model_type, public_key):
        logging.info(self._get_updates.__name__)
        return self.coordinator.get_updates_from_workers(self.workers, model_type, public_key)

    def _federated_averaging(self, updates):
        logging.info(self._federated_averaging.__name__)
        if len(updates) > 0:
            return reduce(sum_collection, updates) / len(self.workers)
        else:
            return 0

    def _send_global_model(self, weights):
        logging.info(self._send_global_model.__name__)
        self.coordinator.send_gradients(self.workers, weights)

    def _get_trained_models(self):
        logging.info(self._get_trained_models.__name__)
        return self.coordinator.get_models_from_workers(self.workers)


def sum_collection(x, y):
    # if len(x) != len(y):
    #     raise ValueError('Vectors must be the same size')

    return x + y
