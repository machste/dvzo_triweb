from sqlalchemy import Column, ForeignKey
from sqlalchemy import Boolean, Integer, Text, Date, Time
from sqlalchemy.orm import relationship

from triweb.models.meta import Base
from triweb.models.user import User
from triweb.models.vehicle import Vehicle


class Workday(Base):
    __tablename__ = 'workdays'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time)
    manager_id = Column(ForeignKey(User.id), nullable=False)
    title = Column(Text, nullable=False)
    vehicle_id = Column(ForeignKey(Vehicle.id))
    description = Column(Text)
    cook = Column(Boolean, nullable=False, server_default='FALSE')
    # Relations to other tables
    manager = relationship(User)
    vehicle = relationship(Vehicle)