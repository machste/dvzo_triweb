from sqlalchemy import Column, ForeignKey
from sqlalchemy import Boolean, Integer, Text, Date, Time
from sqlalchemy.orm import relationship

from triweb.models.meta import Base
from triweb.models.user import User
from triweb.models.vehicle import Vehicle
from triweb.models.workday_user_poll import WorkdayUserPoll
from triweb.models.associations.workday_vehicle import WorkdayVehicle


class Workday(Base):

    __tablename__ = 'workdays'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time)
    manager_id = Column(ForeignKey(User.id), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    cook = Column(Boolean, nullable=False, server_default='FALSE')
    state = Column(Text, nullable=False, server_default='draft')
    archived = Column(Boolean, nullable=False, server_default='FALSE')
    # Relations to other tables
    manager = relationship(User)
    user_polls = relationship(WorkdayUserPoll, back_populates='workday')
    vehicles = relationship(Vehicle, secondary=WorkdayVehicle.__table__)

    STATES = {
        'draft': 'Entwurf',
        'published': 'Veröffentlicht',
        'confirmed': 'Bestätigt',
        'done': 'Erledigt',
        'cancelled': 'Abgesagt'
    }
