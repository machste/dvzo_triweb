from pyramid.view import view_config
from sqlalchemy.exc import SQLAlchemyError

from triweb.views import Private
from triweb.models import User


class UserArchiveView(Private):

    @view_config(route_name='rest.user.archive', permission='administrate',
            renderer='json')
    def view(self):
        user_id = self.request.matchdict['id']
        user = self.dbsession.get(User, user_id)
        if user is None:
            return dict(ok=False)
        user.archived = True
        ok = self.save_user(user)
        return dict(ok=ok, archived=user.archived)

    def save_user(self, user):
        nested_transaction = self.dbsession.begin_nested()
        self.dbsession.add(user)
        try:
            nested_transaction.commit()
        except SQLAlchemyError:
            nested_transaction.rollback()
            return False
        return True
