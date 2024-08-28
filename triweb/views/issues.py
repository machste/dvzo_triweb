from pyramid.view import view_config

from triweb.views import View


class Issues(View):

    @view_config(route_name='issues', renderer='issues.jinja2')
    def view(self):
        #TODO: Get engine data from the DB
        open_issue_lists = {
            'Ed 3/3 401 "Bauma"': 'lok401.open',
            'E 3/3 8518 "Bäretswil"': 'lok18.open',
            'BT Bb 3/5 9': 'lok9.open',
            'Ed 3/4 2 "Hinwil"': 'lok2.open',
            'Ed 3/3 4 "Schwyz"': 'lok4.open',
            'Ee 3/3 16363': 'ee33.open',
            'Tem III 354': 'temiii.open',
            'Tm III 9529': 'tmiii.open',
            'Allgemein & Werkstatt': 'general.open'
        }
        return dict(open_issue_lists=open_issue_lists)
