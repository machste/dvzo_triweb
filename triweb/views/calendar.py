from pyramid.view import view_config

from triweb.views import View


class Calendar(View):

    @view_config(route_name='calendar', renderer='calendar.jinja2')
    def view(self):
        return {}
