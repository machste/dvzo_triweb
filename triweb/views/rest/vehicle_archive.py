from pyramid.view import view_config
from sqlalchemy.exc import SQLAlchemyError

from triweb.views import Private
from triweb.models import Vehicle


class VehicleArchiveView(Private):

    @view_config(route_name='rest.vehicle.archive', permission='administrate',
            renderer='json')
    def view(self):
        vehicle_id = self.request.matchdict['id']
        vehicle = self.dbsession.get(Vehicle, vehicle_id)
        if vehicle is None:
            return dict(ok=False)
        vehicle.archived = True
        ok = self.save_vehicle(vehicle)
        return dict(ok=ok, archived=vehicle.archived)

    def save_vehicle(self, vehicle):
        nested_transaction = self.dbsession.begin_nested()
        self.dbsession.add(vehicle)
        try:
            nested_transaction.commit()
        except SQLAlchemyError:
            nested_transaction.rollback()
            return False
        return True
