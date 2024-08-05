from pyramid.view import view_config

from triweb.views import View


class Issues(View):

    @view_config(route_name='issues', renderer='issues.jinja2')
    def view(self):
        jira = self.request.jira
        done = jira.get_issues('done')
        doing = jira.get_issues('doing')
        open_per_engine = {
            'Ed 3/3 401 "Bauma"': jira.get_issues('lok401.open'),
            'E 3/3 8518 "Bäretswil"': jira.get_issues('lok18.open'),
            'BT Bb 3/5 9': jira.get_issues('lok9.open'),
            'Ed 3/4 2 "Hinwil"': jira.get_issues('lok2.open'),
            'Ed 3/3 4 "Schwyz"': jira.get_issues('lok4.open'),
            'Ee 3/3 16363': jira.get_issues('ee33.open'),
            'Tem III 354"': jira.get_issues('temiii.open'),
            'Tm III 9529': jira.get_issues('tmiii.open')
        }
        return dict(done=done, doing=doing, open_per_engine=open_per_engine)
