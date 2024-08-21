from pyramid.view import view_config

from triweb.views import View


class Issues(View):

    @view_config(route_name='rest.issues', renderer='json')
    def view(self):
        data = { 'issues': [] }
        list_name = self.request.matchdict['list_name']
        if list_name is None:
            return data
        issues = self.request.jira.get_issues(list_name)
        if issues is None:
            return data
        data['issues'] = issues
        return data
