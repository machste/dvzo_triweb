from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, Text, Boolean
from sqlalchemy.orm import relationship

from triweb.models.meta import Base
from triweb.models.vehicle_manager import VehicleManager


class Vehicle(Base):

    __tablename__ = 'vehicles'

    TYPE = 'Fahrzeug'

    id = Column(Integer, primary_key=True)
    type = Column(Text, nullable=False, server_default='vehicle')
    name = Column(Text, nullable=False)
    number = Column(Integer)
    nvr = Column(Text)
    token = Column(Text, unique=True)
    given_name = Column(Text)
    short_name = Column(Text)
    state = Column(Text, nullable=False, server_default='unknown')
    station = Column(Text)
    track = Column(Text)
    space = Column(Text)
    manager_id = Column(ForeignKey(VehicleManager.id))
    # Relations to other tables
    manager = relationship(VehicleManager, back_populates='vehicles')

    __mapper_args__ = {
        "polymorphic_identity": "vehicle",
        "polymorphic_on": "type",
    }

    STATES = {
        'operative': 'In Betrieb',
        'winterised': 'Eingewintert',
        'out_of_order': 'Ausser Betrieb',
        'unknown': 'Unbekannt'
    }

    @property
    def display_name(self):
        dname = self.name
        if self.number is not None:
            dname += f' {self.number}'
        if self.given_name is not None:
            dname += f' "{self.given_name}"'
        return dname

    def copy_from(self, other, copy_id=False):
        self.name = other.name
        self.number = other.number
        self.nvr = other.nvr
        self.token = other.token
        self.given_name = other.given_name
        self.short_name = other.short_name
        self.state = other.state
        self.station = other.station
        self.track = other.track
        self.space = other.space
        self.manager_id = other.manager_id

    @staticmethod
    def get_types():
        types = {}
        for id, mapper in Vehicle.__mapper__.polymorphic_map.items():
            types[id] = mapper.class_.TYPE
        return types

    @staticmethod
    def create_from_type(identity):
        for id, mapper in Vehicle.__mapper__.polymorphic_map.items():
            if id == identity:
                return mapper.class_()
        return Vehicle()


class SteamLoco(Vehicle):

    __tablename__ = "steam_locos"

    TYPE = 'Dampflokomotive'

    id = Column(ForeignKey(Vehicle.id), primary_key=True)
    boiler_emtpy = Column(Boolean, nullable=False, server_default='TRUE')
    check_leakage = Column(Boolean, nullable=False, server_default='TRUE')

    __mapper_args__ = {
        "polymorphic_identity": "steam",
    }


class ElectricLoco(Vehicle):

    __tablename__ = "electric_locos"

    TYPE = 'Elektrolokomotive'

    id = Column(ForeignKey(Vehicle.id), primary_key=True)
    electric_break = Column(Boolean, nullable=False, server_default='FALSE')

    __mapper_args__ = {
        "polymorphic_identity": "electric",
    }


class DieselLoco(Vehicle):

    __tablename__ = "diesel_locos"

    TYPE = 'Diesellokomotive'

    id = Column(ForeignKey(Vehicle.id), primary_key=True)
    low_fuel = Column(Boolean, nullable=False, server_default='TRUE')

    __mapper_args__ = {
        "polymorphic_identity": "diesel",
    }
