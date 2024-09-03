from sqlalchemy import Column, ForeignKey
from sqlalchemy import Boolean, Integer, Text, Date, Time

from triweb.models.meta import Base
from triweb.models.user import User


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

