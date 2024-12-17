from pyramid.view import view_config

from triweb.views import Private
from triweb.models.workday import Workday


class Workdays(Private):

    @view_config(route_name='workdays', renderer='workdays.jinja2')
    def view(self):
        workdays = self.dbsession.query(Workday).order_by(Workday.date).all()
        return dict(workdays=workdays, states=Workday.STATES)
