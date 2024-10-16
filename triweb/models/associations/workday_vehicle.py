from sqlalchemy import Column, ForeignKey

from triweb.models.meta import Base


class WorkdayVehicle(Base):

    __tablename__ = 'workday_vehicle_associations'

    workday_id = Column(ForeignKey('workdays.id'), primary_key=True)
    vehicle_id = Column(ForeignKey('vehicles.id'), primary_key=True)
