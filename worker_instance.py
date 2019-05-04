class WorkerInstance(object):

    def __init__(self, data):
        self.id = data['id']
        self.host = data['host']
        self.port = data['port']
