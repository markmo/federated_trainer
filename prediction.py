import uuid


class Prediction(object):

    def __init__(self, values, mse=None):
        self.id = str(uuid.uuid1())
        self.values = values
        self.mse = mse

    def serialize(self):
        return {
            'id': self.id,
            'values': self.values,
            'mse': self.mse
        }
