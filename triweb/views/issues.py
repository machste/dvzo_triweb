from pyramid.view import view_config

from triweb.views import Private
from triweb.models import Vehicle


class Issues(Private):

    @view_config(route_name='issues', renderer='issues.jinja2')
    def view(self):
        open_issue_lists = {}
        engines = self.dbsession.query(Vehicle).\
            filter(Vehicle.token != None).all()
        for engine in engines:
            open_issue_lists[engine.display_name] = f'{engine.token}.open'
        open_issue_lists['Allgemein & Werkstatt'] = 'general.open'
        return dict(open_issue_lists=open_issue_lists)
