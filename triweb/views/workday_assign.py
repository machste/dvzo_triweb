from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden

from triweb.views import Private
from triweb.models.workday import Workday
from triweb.errors import DatabaseError


class WorkdayAssignView(Private):

    def __init__(self, request):
        super().__init__(request)

    @view_config(route_name='workday.assign', permission='lead',
            renderer='workday_assign.jinja2')
    def view_assign(self):
        workday_id = self.request.matchdict['id']
        workday = self.dbsession.get(Workday, workday_id)
        if workday is None:
            raise DatabaseError(f"Arbeitstag mit ID: '{workday_id}' nicht gefunden!")
        # Check ownership for permissions less than manager
        if not self.request.has_permission('manage') \
                and self.request.identity.id != workday.manager_id:
            raise HTTPForbidden()
        return dict(workday=workday)
