from pyramid.view import view_config

from triweb.views import View


class Workdays(View):

    @view_config(route_name='workdays', renderer='workdays.jinja2')
    def view(self):
        return {}
