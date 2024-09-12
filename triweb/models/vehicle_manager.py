from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, Text
from sqlalchemy.orm import relationship

from triweb.models.meta import Base
from triweb.models.user import User


class VehicleManager(Base):
    __tablename__ = 'vehicle_managers'
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(User.id), nullable=False, unique=True)
    badge_color = Column(Text)
    # Relations to other tables
    user = relationship(User)
    vehicles = relationship("Vehicle", back_populates='manager')

    @property
    def display_name(self):
        if self.user is not None:
            return self.user.display_name
        return ''
