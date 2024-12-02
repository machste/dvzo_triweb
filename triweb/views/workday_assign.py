from pyramid.view import view_config

from triweb.views import Private
from triweb.models.workday import Workday
from triweb.errors import DatabaseError


class WorkdayAssignView(Private):

    def __init__(self, request):
        super().__init__(request)

    @view_config(route_name='workday.assign', permission='manage',
            renderer='workday_assign.jinja2')
    def view_assign(self):
        workday_id = self.request.matchdict['id']
        workday = self.dbsession.get(Workday, workday_id)
        if workday is None:
            raise DatabaseError(f"Arbeitstag mit ID: '{workday_id}' nicht gefunden!")
        return dict(workday=workday)
