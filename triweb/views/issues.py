from pyramid.view import view_config

from triweb.views import View


class Issues(View):

    @view_config(route_name='issues', renderer='issues.jinja2')
    def view(self):
        return {}
