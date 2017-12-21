
class Transaction(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    
    @property
    def value(self):
        return vars(self)
