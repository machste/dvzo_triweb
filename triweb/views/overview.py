from pyramid.view import view_config

from triweb.views import Private
from triweb.models.vehicle import SteamLoco, ElectricLoco, DieselLoco


class Overview(Private):

    STATE_BADGE_COLORS = {
        'operative': 'success',
        'winterised': 'info',
        'out_of_order': 'danger',
        'unknown': 'warning'
    }

    @view_config(route_name='overview', renderer='overview.jinja2')
    def view(self):
        steam_locos = self.dbsession.query(SteamLoco).all()
        electric_locos = self.dbsession.query(ElectricLoco).all()
        diesel_locos = self.dbsession.query(DieselLoco).all()
        return dict(steam_locos=steam_locos, electric_locos=electric_locos,
                diesel_locos=diesel_locos,
                state_badge_colors=self.STATE_BADGE_COLORS)
