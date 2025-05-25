class LogError(Exception):
    def __init__(self, message, **kwargs):
        super().__init__(self, message, **kwargs)
        

class SqlInitError(Exception):
    def __init__(self, message, **kwargs):
        super().__init__(self, message, **kwargs)
