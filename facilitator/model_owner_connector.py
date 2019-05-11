import logging

import requests


class ModelOwnerConnector(object):

    def __init__(self, model_deployer_port):
        logging.debug('init with model_deployer_port={}'.format(model_deployer_port))
        self.model_deployer_port = model_deployer_port
        self.remote_addr = None
        self.model_id = None

    def send_model_update(self, params):
        logging.debug(self.send_model_update.__name__)
        url = 'http://{}:{}/models/{}'.format(self.remote_addr, self.model_deployer_port, self.model_id)
        if logging.getLogger().getEffectiveLevel() == 'DEBUG':
            logging.info('Calling {} [PATCH] with:\n{}'.format(url, params))
        else:
            logging.info('Calling {} [PATCH]'.format(url))

        response = requests.patch(url, json=params)
        return response.json()

    def send_model_finished(self, params):
        logging.debug(self.send_model_finished.__name__)
        url = 'http://{}:{}/model_finished/{}'.format(self.remote_addr, self.model_deployer_port, self.model_id)
        if logging.getLogger().getEffectiveLevel() == 'DEBUG':
            logging.info('Calling {} [PUT] with:\n{}'.format(url, params))
        else:
            logging.info('Calling {} [PUT]'.format(url))

        requests.put(url, json=params)
