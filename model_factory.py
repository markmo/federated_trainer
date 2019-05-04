from enum import Enum
from linear_regression import LinearRegression


class ModelType(Enum):
    LINEAR_REGRESSION = 1


class InvalidModelException(Exception):

    def __init__(self, model_type, status_code=400):
        message = 'Invalid model type {}'.format(model_type)
        super().__init__(message)
        self.status_code = status_code


class ModelFactory(object):

    @classmethod
    def get_model(cls, model_type):
        if ModelType[model_type] == ModelType.LINEAR_REGRESSION:
            return LinearRegression
        else:
            raise InvalidModelException(model_type)
