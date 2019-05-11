import logging

from common.metrics import mean_squared_error
from model_base import ModelBase
from prediction import Prediction


class LinearRegression(ModelBase):
    """
    Run linear regression either with local data or by gradient steps, where gradients
    can be sent from a remote host.
    """

    def fit(self, n_iter, eta=0.01):
        """ Fit the model """
        logging.info(self.fit.__name__)
        for i in range(n_iter):
            logging.info('Epoch {}'.format(i + 1))
            grad = self.compute_gradient()
            self.gradient_step(grad, eta)

        return self.params

    def compute_gradient(self):
        """ Return the gradient computed for the current model on all training data """
        logging.info(self.compute_gradient.__name__)
        logging.debug('self.x shape: {}'.format(self.x.shape))
        pred = self.predict(self.x)
        logging.debug('pred shape: {}'.format(pred.values.shape))
        error = pred.values - self.y
        logging.debug('error shape: {}'.format(error.shape))
        return error.dot(self.x) / len(self.x)

    def gradient_step(self, gradient, eta=0.01):
        """ Update the model with the given gradient """
        logging.info(self.gradient_step.__name__)
        logging.debug('gradient shape: {}'.format(gradient.shape))
        logging.debug('self.params before step shape: {}'.format(self.params.shape))
        self.params = self.params - (eta * gradient)
        logging.debug('self.params after step shape:  {}'.format(self.params.shape))
        return self.params

    # def calculate_cost(self, error):
    #     return 1 / (2 * len(self.x)) * np.dot(error.T, error)

    def predict(self, x, y_test=None):
        """ Score """
        logging.debug(self.predict.__name__)
        logging.debug('self.params shape: {}'.format(self.params.shape))
        values = x.dot(self.params)
        mse = mean_squared_error(values, y_test) if y_test is not None else None
        return Prediction(values, mse)
