import logging

from pyramid.view import view_config
from sqlalchemy.exc import SQLAlchemyError

from triweb.views import Private
from triweb.models import WorkdayUserPoll

_log = logging.getLogger(__name__)


class WorkdayPollView(Private):

    @view_config(route_name='rest.workday.poll', renderer='json')
    def view(self):
        workday_id = self.request.matchdict['id']
        user_id = self.request.identity.id
        state = self.get_param_state()
        if state == 'invalid':
            return dict(ok=False)
        ok = True
        poll = self.dbsession.get(WorkdayUserPoll, (workday_id, user_id))
        # If there is no poll yet, ...
        if poll is None:
            # ... create one.
            poll = WorkdayUserPoll(workday_id=workday_id, user_id=user_id)
            poll.fixed = False
            ok = False
        changed = False
        # If a new state is defined, ...
        if state is not None and state != poll.state:
            # ... change the state of the poll.
            poll.state = state
            changed = True
        # If the poll changed, ...
        if changed:
            # ... save it.
            ok = self.save_poll(poll)
        return dict(ok=ok, state=poll.state, fixed=poll.fixed)

    def get_param_state(self):
        state = self.request.params.get('state')
        if state is not None:
            if state not in WorkdayUserPoll.STATES:
                _log.warn(f"Got invalid poll state '{state}'!")
                state = 'invalid'
        return state

    def save_poll(self, poll):
        nested_transaction = self.dbsession.begin_nested()
        self.dbsession.add(poll)
        try:
            nested_transaction.commit()
        except SQLAlchemyError:
            nested_transaction.rollback()
            return False
        return True
