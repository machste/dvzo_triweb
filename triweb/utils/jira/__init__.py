import logging
import requests
import time

from requests.auth import HTTPBasicAuth

from triweb.utils.jira.issue import Issue
from triweb.errors import GeneralError

_log = logging.getLogger(__name__)


class Jira(object):

    FILTERS = {
        'lok2.open': 10012,
        'lok4.open': 10014,
        'lok9.open': 10010,
        'lok18.open': 10015,
        'lok401.open': 10011,
        'ee33.open': 10016,
        'tmiii.open': 10018,
        'temiii.open': 10017,
        'doing': 10023,
        'done': 10028
    }

    def __init__(self, url):
        self.url = url
        self.headers = { 'Accept': 'application/json' }
        self.auth = None
        self.issue_cache = None

    def set_auth(self, user, token):
        self.auth = HTTPBasicAuth(user, token)

    def set_issue_cache(self, cache):
        self.issue_cache = cache

    def request(self, path):
        url = self.url + path
        res = requests.request('GET', url=url, auth=self.auth,
                headers=self.headers)
        if not res.ok:
            raise self.Error("Request '{url}' failed!")
        return res.json()

    def get_issues(self, list_name, max_age=None):
        # Check the issue cache first
        issues = None
        if self.issue_cache is not None:
            issues = self.issue_cache.get_issues(list_name, max_age)
        if issues is not None:
            _log.debug(f"Request '{list_name}' hit issue cache.")
            return issues
        # Otherwise get the issues from Jira
        issues = []
        filter_id = self.FILTERS[list_name]
        path = f'/rest/api/3/search?&fields=issuetype,status,priority,summary,created,duedate,resolutiondate,customfield_10058,customfield_10069&jql=filter%3D{filter_id}'
        js = self.request(path)
        js_issues = js['issues']
        _log.info(f"Get issues '{list_name}' (id: {filter_id}) ...")
        for js_issue in js_issues:
            issue = Issue.from_js(js_issue)
            issues.append(issue)
            _log.debug(f'Got issue {issue}')
        # Update issue cache
        if self.issue_cache is not None:
            self.issue_cache.update_issues(list_name, issues)
        return issues


    class Error(GeneralError):
        pass


class IssueCache(object):

    def __init__(self):
        self.max_age = 3600
        self.data = {}

    def get_issues(self, name, max_age=None):
        max_age = max_age or self.max_age
        d = self.data.get(name, None)
        if d is None:
            return None
        if time.time() - d.timestamp > max_age:
            del self.data[name]
            return None
        return d.issues

    def update_issues(self, name, issues):
        self.data[name] = self.Data(issues)

    
    class Data(object):

        def __init__(self, issues):
            self.issues = issues
            self.timestamp = time.time()


def install_jira(config):
    _log.debug('Install Jira API')
    settings = config.get_settings()
    url = settings.get('jira.url', 'https://atlassian.net')
    user = settings.get('jira.user')
    token = settings.get('jira.token')
    issue_cache = IssueCache()
    def jira_factory(request):
        _log.debug('Create Jira API')
        jira = Jira(url)
        jira.set_issue_cache(issue_cache)
        if user is not None and token is not None:
            jira.set_auth(user, token)
        return jira
    config.add_request_method(jira_factory, 'jira', reify=True)