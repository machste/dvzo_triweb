from sqlalchemy import Column, ForeignKey
from sqlalchemy import Text, Boolean
from sqlalchemy.orm import relationship

from triweb.models.meta import Base


class WorkdayUserPoll(Base):

    __tablename__ = 'workday_user_polls'

    workday_id = Column(ForeignKey('workdays.id'), primary_key=True)
    user_id = Column(ForeignKey('users.id'), primary_key=True)
    state = Column(Text)
    fixed = Column(Boolean, nullable=False, server_default='FALSE')
    # Relations to other tables
    workday = relationship('Workday')
    user = relationship('User')

    STATES = {
        'invalid': 'Ungültig',
        'no': 'Nein',
        'possible': 'Möglich',
        'yes': 'Ja'
    }
