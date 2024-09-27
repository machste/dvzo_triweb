import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound

from triweb.views import Private

_log = logging.getLogger(__name__)


class Issue(Private):

    @view_config(route_name='issue', renderer='issue.jinja2')
    def view(self):
        issue_id = self.request.matchdict['id']
        max_age = self.request.params.get('max_age')
        if max_age is not None:
            try:
                max_age = int(max_age)
            except:
                _log.warn(f"Expected int for max_age not '{max_age}'!")
                max_age = None
        # Get issue from jira
        issue = self.request.jira.get_issue(issue_id, max_age)
        if issue is None:
            raise HTTPNotFound()
        return dict(issue=issue)
