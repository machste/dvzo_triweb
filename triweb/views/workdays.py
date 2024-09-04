from pyramid.view import view_config

from triweb.views import View
from triweb.models.workday import Workday


class Workdays(View):

    @view_config(route_name='workdays', permission='manage',
            renderer='workdays.jinja2')
    def view(self):
        workdays = self.dbsession.query(Workday).order_by(Workday.date).all()
        return dict(workdays=workdays)
