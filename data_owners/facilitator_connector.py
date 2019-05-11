import logging

import requests


class FacilitatorConnector(object):

    def __init__(self, conf):
        logging.debug('init with:\n{}'.format(conf))
        self.federated_trainer_host = conf['federated_trainer_host']

    def register(self, worker_data):
        logging.debug(self.register.__name__)
        registration_url = self.federated_trainer_host + '/workers'
        logging.info("Registering client '{}' with server '{}'".format(worker_data['id'], registration_url))
        response = requests.post(registration_url, json=worker_data)
        response.raise_for_status()
        return response.json()
