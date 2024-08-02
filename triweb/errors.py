class GeneralError(Exception):

    def __init__(self, msg):
        self.msg = msg


class DatabaseError(GeneralError):
    pass
