class GeneralError(Exception):

    TOPIC = None

    def __init__(self, msg):
        self.topic = self.TOPIC
        self.msg = msg


class DatabaseError(GeneralError):
    
    TOPIC = 'Datenbank Fehler'
