from pyramid.view import view_config

from triweb.views import Private


class JiraCacheCleanView(Private):

    @view_config(route_name='rest.jira.cache.clear', permission='administrate',
            renderer='json')
    def view(self):
        ok = self.request.jira.clear_cache()
        return dict(ok=ok)
