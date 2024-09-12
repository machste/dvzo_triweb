from pyramid.view import view_config

from triweb.views import Private
from triweb.models.vehicle_manager import VehicleManager


class VehicleManagers(Private):

    @view_config(route_name='vehicle_managers',
            renderer='vehicle_managers.jinja2')
    def view(self):
        vehicle_managers = self.dbsession.query(VehicleManager).all()
        return dict(vehicle_managers=vehicle_managers)
