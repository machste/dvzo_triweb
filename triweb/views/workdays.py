from pyramid.view import view_config

from triweb.views import Private
from triweb.models.workday import Workday


class Workdays(Private):

    @view_config(route_name='workdays', renderer='workdays.jinja2')
    def view(self):
        workdays = self.dbsession.query(Workday).\
                filter(Workday.archived == False).\
                order_by(Workday.date.desc()).all()
        return dict(workdays=workdays, states=Workday.STATES)
