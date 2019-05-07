import logging
import numpy as np


class LinearRegression(object):
    """
    Run linear regression either with local data or by gradient steps, where gradients
    can be sent from a remote host.
    """

    def __init__(self, x, y):
        logging.debug('init')
        self.x, self.y = np.asarray(x), np.asarray(y)
        self.weights = np.zeros(self.x.shape[1])

    def set_weights(self, weights):
        logging.debug(self.set_weights.__name__)
        self.weights = np.asarray(weights)

    def fit(self, n_epochs, eta=0.01):
        """ Fit the model """
        logging.debug(self.fit.__name__)
        for _ in range(n_epochs):
            grad = self.compute_gradient()
            self.gradient_step(grad, eta)

    def gradient_step(self, gradient, eta=0.01):
        """ Update the model with the given gradient """
        logging.debug(self.gradient_step.__name__)
        logging.debug('gradient shape: {}'.format(gradient.shape))
        logging.debug('self.weights before step shape: {}'.format(self.weights.shape))
        self.weights = self.weights - (eta * gradient)
        logging.debug('self.weights after step shape:  {}'.format(self.weights.shape))

    def compute_gradient(self):
        """ Return the gradient computed for the current model on all training data """
        logging.debug(self.compute_gradient.__name__)
        logging.debug('self.x shape: {}'.format(self.x.shape))
        pred = self.predict(self.x)
        logging.debug('pred shape: {}'.format(pred.shape))
        error = pred - self.y
        logging.debug('error shape: {}'.format(error.shape))

        # can't handle EncryptedNumbers
        # cost = self.calculate_cost(error)
        # logging.info('cost: {}'.format(cost))
        # mse = mean_squared_error(pred, self.y)
        # logging.info('mse: {}'.format(mse))

        return error.dot(self.x) / len(self.x)

    def calculate_cost(self, error):
        return 1 / (2 * len(self.x)) * np.dot(error.T, error)

    def predict(self, x):
        """ Score """
        logging.debug(self.predict.__name__)
        logging.debug('self.weights shape: {}'.format(self.weights.shape))
        return x.dot(self.weights)


def mean_squared_error(y_pred, y):
    return np.mean((y_pred - y)**2)
