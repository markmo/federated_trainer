import logging
import requests


class FederatedTrainerConnector(object):

    def __init__(self, conf):
        logging.info('init with:\n{}'.format(conf))
        self.federated_trainer_host = conf['federated_trainer_host']

    def register(self, worker_data):
        logging.info(self.register.__name__)
        registration_url = self.federated_trainer_host + '/workers'
        logging.info("Registering client '{}' with server '{}'".format(worker_data['id'], registration_url))
        response = requests.post(registration_url, json=worker_data)
        response.raise_for_status()
        return response.json()
