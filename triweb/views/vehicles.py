from pyramid.view import view_config

from triweb.views import Private
from triweb.models.vehicle import Vehicle


class Vehicles(Private):

    @view_config(route_name='vehicles', renderer='vehicles.jinja2')
    def view(self):
        vehicles = self.dbsession.query(Vehicle).all()
        return dict(vehicles=vehicles)
