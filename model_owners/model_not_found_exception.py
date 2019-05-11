class ModelNotFoundException(Exception):

    def __init__(self, model_id, status_code=404):
        message = 'Model ({}) not found'.format(model_id)
        super().__init__(message)
        self.status_code = status_code
