from pyramid.view import view_config

from triweb.views import Private


class Settings(Private):

    @view_config(route_name='settings', renderer='settings.jinja2')
    def view(self):
        return dict()
