from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther, HTTPForbidden
from sqlalchemy.exc import SQLAlchemyError

from triweb.views import Private
from triweb.models.workday import Workday
from triweb.utils.toast import Toast
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
        if 'form.submitted' in self.request.params:
            new_state = self.request.params.get('state')
            if new_state in Workday.STATES:
                workday.state = new_state
                self.save_workday(workday)
                self.push_toast('Die Einteilung für den Arbeitstag wurde bestätigt!',
                        title='Einteilung bestätigt!', type=Toast.Type.SUCCESS)
            else:
                self.push_toast('Die Einteilung für konnte nicht vorgenommen werden!',
                        title='Fehler!', type=Toast.Type.DANGER)
            return HTTPSeeOther(self.request.route_url('calendar'))
        return dict(workday=workday)


    def save_workday(self, workday):
        nested_transaction = self.dbsession.begin_nested()
        self.dbsession.add(workday)
        try:
            nested_transaction.commit()
        except SQLAlchemyError as err:
            nested_transaction.rollback()
            raise DatabaseError(str(err))
        return workday
