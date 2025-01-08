from pyramid.view import view_config

from triweb.views import Private
from triweb.utils.db import get_managed_vehicles
from triweb.models.vehicle import SteamLoco, ElectricLoco, DieselLoco


class Issues(Private):

    @view_config(route_name='issues', renderer='issues.jinja2')
    def view(self):
        open_issue_lists = {}
        locos = get_managed_vehicles(self.dbsession,
                order=(SteamLoco, ElectricLoco, DieselLoco))
        open_issue_lists['Allgemein & Werkstatt'] = 'general.open'
        for loco in locos:
            open_issue_lists[loco.display_name] = f'{loco.token}.open'
        return dict(open_issue_lists=open_issue_lists)
