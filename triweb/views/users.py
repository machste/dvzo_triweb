from pyramid.view import view_config

from triweb.views import Private
from triweb.models.user import User


class Users(Private):

    @view_config(route_name='users', permission="administrate",
            renderer='users.jinja2')
    def view(self):
        users = self.dbsession.query(User).\
            filter(User.archived == False).all()
        return dict(users=users, roles=User.ROLES)
