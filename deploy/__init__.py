__VERSION__ = '1.0'


class FabricException(Exception):

    """ Fabric exception class
    """

    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)
