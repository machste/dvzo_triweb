import logging

from pyramid.view import view_config
from sqlalchemy.exc import SQLAlchemyError

from triweb.views import Private
from triweb.models import Workday

_log = logging.getLogger(__name__)


class WorkdayStateView(Private):

    @view_config(route_name='rest.workday.state', permission='lead',
            renderer='json')
    def view(self):
        workday_id = self.request.matchdict['id']
        state = self.get_param_state()
        if state == 'invalid':
            return dict(ok=False)
        workday = self.dbsession.get(Workday, workday_id)
        if workday is None:
            return dict(ok=False)
        # Check ownership for permissions less than manager
        if not self.request.has_permission('manage') \
                and self.request.identity.id != workday.manager_id:
            return dict(ok=False)
        ok = True
        if state is not None and state != workday.state:
            # Set new state and save it.
            workday.state = state
            ok = self.save_workday(workday)
        return dict(ok=ok, state=workday.state)

    def get_param_state(self):
        state = self.request.params.get('state')
        if state is not None:
            if state not in Workday.STATES:
                _log.warn(f"Got invalid workday state '{state}'!")
                state = 'invalid'
        return state

    def save_workday(self, workday):
        nested_transaction = self.dbsession.begin_nested()
        self.dbsession.add(workday)
        try:
            nested_transaction.commit()
        except SQLAlchemyError:
            nested_transaction.rollback()
            return False
        return True
