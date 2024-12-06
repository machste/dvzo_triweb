import logging

from pyramid.view import view_config
from sqlalchemy.exc import SQLAlchemyError

from triweb.views import Private
from triweb.models import WorkdayUserPoll

_log = logging.getLogger(__name__)


class WorkdayAssignView(Private):

    @view_config(route_name='rest.workday.assign', permission='manage',
            renderer='json')
    def view(self):
        workday_id = self.request.matchdict['id']
        state = self.get_param_state()
        user_id = self.get_param_user()
        if user_id is None:
            return dict(ok=False)
        poll = self.dbsession.get(WorkdayUserPoll, (workday_id, user_id))
        if poll is None:
            return dict(ok=False)
        poll.fixed = state
        ok = self.save_poll(poll)
        return dict(ok=ok, state=poll.state, fixed=poll.fixed)

    def get_param_user(self):
        user = self.request.params.get('user')
        if user is not None:
            try:
                return int(user)
            except:
                return None
        return self.request.identity.id

    def get_param_state(self):
        state = self.request.params.get('state')
        if state is not None and state == 'false':
            return False
        return True

    def save_poll(self, poll):
        nested_transaction = self.dbsession.begin_nested()
        self.dbsession.add(poll)
        try:
            nested_transaction.commit()
        except SQLAlchemyError:
            nested_transaction.rollback()
            return False
        return True
