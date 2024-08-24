import logging

from pyramid.view import view_config

from triweb.views import View

_log = logging.getLogger(__name__)

class Issues(View):

    @view_config(route_name='rest.issues', renderer='json')
    def view(self):
        max_age = self.request.params.get('max_age')
        if max_age is not None:
            try:
                max_age = int(max_age)
            except:
                _log.warn(f"Expected int for max_age not '{max_age}'!")
                max_age = None
        data = { 'issues': [] }
        list_name = self.request.matchdict['list_name']
        if list_name is None:
            return data
        issues = self.request.jira.get_issues(list_name, max_age)
        if issues is None:
            return data
        data['issues'] = issues
        return data
