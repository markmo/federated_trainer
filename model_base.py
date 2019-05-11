import logging

import numpy as np


class ModelBase(object):

    def __init__(self, x=None, y=None):
        logging.debug('init')
        self.x, self.y = x, y
        self.params = np.zeros(x.shape[1]) if x is not None else None

    def fit(self, n_iter, eta=0.01):
        pass

    def predict(self, x):
        pass
