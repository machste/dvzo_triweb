from pyramid.view import view_config

from triweb.views import View


class Issues(View):

    @view_config(route_name='issues', renderer='issues.jinja2')
    def view(self):
        done = self.request.jira.get_issues('done')
        doing = self.request.jira.get_issues('doing')
        lok401 = self.request.jira.get_issues('lok401.open')
        return dict(done=done, doing=doing, lok401=lok401)
