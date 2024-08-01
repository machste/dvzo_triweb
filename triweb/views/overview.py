from pyramid.view import view_config

from triweb.views import View


class Overview(View):

    @view_config(route_name='overview', renderer='overview.jinja2')
    def view(self):
        return {}
