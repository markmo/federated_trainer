import logging
import numpy as np


class LinearRegression(object):

    def __init__(self, x, y):
        logging.info('init')
        self.x, self.y = np.asarray(x), np.asarray(y)
        self.weights = np.zeros(self.x.shape[1])

    def set_weights(self, weights):
        logging.info(self.set_weights.__name__)
        self.weights = np.asarray(weights)

    def fit(self, n_epochs, eta=0.01):
        logging.info(self.fit.__name__)
        for _ in range(n_epochs):
            grad = self.compute_gradient()
            self.gradient_step(grad, eta)

    def gradient_step(self, gradient, eta=0.01):
        logging.info(self.gradient_step.__name__)
        logging.info('gradient shape: {}'.format(gradient.shape))
        logging.info('self.weights before step shape: {}'.format(self.weights.shape))
        self.weights = self.weights - (eta * gradient)
        logging.info('self.weights after step shape:  {}'.format(self.weights.shape))

    def compute_gradient(self):
        logging.info(self.compute_gradient.__name__)
        logging.info('self.x shape: {}'.format(self.x.shape))
        pred = self.predict(self.x)
        logging.info('pred shape: {}'.format(pred.shape))
        delta = pred - self.y
        logging.info('delta shape: {}'.format(delta.shape))
        return delta.dot(self.x) / len(self.x)

    def predict(self, x):
        logging.info(self.predict.__name__)
        logging.info('self.weights shape: {}'.format(self.weights.shape))
        return x.dot(self.weights)
