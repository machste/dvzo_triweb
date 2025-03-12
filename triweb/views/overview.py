from pyramid.view import view_config

from triweb.views import Private
from triweb.models.vehicle import SteamLoco, ElectricLoco, DieselLoco
from triweb.utils.db import get_managed_vehicles

class Overview(Private):

    STATE_BADGE_COLORS = {
        'operative': 'success',
        'winterised': 'info',
        'suspended': 'danger',
        'out_of_order': 'danger',
        'unknown': 'warning'
    }

    @view_config(route_name='overview', renderer='overview.jinja2')
    def view(self):
        steam_locos = get_managed_vehicles(self.dbsession, (SteamLoco, ))
        electric_locos = get_managed_vehicles(self.dbsession, (ElectricLoco, ))
        diesel_locos = get_managed_vehicles(self.dbsession, (DieselLoco, ))
        return dict(steam_locos=steam_locos, electric_locos=electric_locos,
                diesel_locos=diesel_locos,
                state_badge_colors=self.STATE_BADGE_COLORS)
