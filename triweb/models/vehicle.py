from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, Text
from sqlalchemy.orm import relationship

from triweb.models.meta import Base
from triweb.models.vehicle_manager import VehicleManager


class Vehicle(Base):
    __tablename__ = 'vehicles'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    number = Column(Integer)
    nvr = Column(Text)
    token = Column(Text, unique=True)
    given_name = Column(Text)
    short_name = Column(Text)
    manager_id = Column(ForeignKey(VehicleManager.id))
    # Relations to other tables
    manager = relationship(VehicleManager, back_populates='vehicles')

    @property
    def display_name(self):
        dname = self.name
        if self.number is not None:
            dname += f' {self.number}'
        if self.given_name is not None:
            dname += f' "{self.given_name}"'
        return dname
