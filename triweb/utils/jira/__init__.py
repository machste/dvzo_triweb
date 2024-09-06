import logging
import requests
import time

from requests.auth import HTTPBasicAuth

from triweb.utils.jira.issue import Issue
from triweb.errors import GeneralError

_log = logging.getLogger(__name__)


class Jira(object):

    FILTERS = {
        'lok2.open': 10030,
        'lok4.open': 10033,
        'lok9.open': 10026,
        'lok18.open': 10025,
        'lok401.open': 10024,
        'ee33.open': 10032,
        'tmiii.open': 10018,
        'temiii.open': 10031,
        'general.open': 10027,
        'doing': 10023,
        'done': 10028
    }

    def __init__(self, url):
        self.url = url
        self.headers = { 'Accept': 'application/json' }
        self.auth = None
        self.cache = None

    def set_auth(self, user, token):
        self.auth = HTTPBasicAuth(user, token)

    def set_cache(self, cache):
        self.cache = cache

    def request(self, path):
        url = self.url + path
        res = requests.request('GET', url=url, auth=self.auth,
                headers=self.headers)
        if not res.ok:
            _log.error(f"Request '{url}' failed!")
            raise self.Error(f"Anfrage bei '{self.url}' hat fehlgeschlagen!")
        return res.json()

    def get_issue(self, id, max_age=None):
        # Check the issue cache
        if self.cache is not None:
            issue = self.cache.get_data('issues', id, max_age)
        if issue is not None:
            _log.debug(f"Request for issue #{id} hit cache.")
            return issue
        # Otherwise get the issue from Jira
        path = f'/rest/api/3/issue/{id}'
        js_issue = self.request(path)
        issue = Issue.from_jira_js(js_issue)
        _log.debug(f'Got issue {issue}')
        # Update cache
        if self.cache is not None:
            self.cache.update_data('issues', id, issue)
        return issue

    def get_issues(self, list_name, max_age=None):
        # Check list name
        try:
            filter_id = self.FILTERS[list_name]
        except:
            _log.error(f"Issue list '{list_name}' does not exist!")
            return None
        # Check the issue cache
        if self.cache is not None:
            issues = self.cache.get_data('issue_lists', list_name, max_age)
        if issues is not None:
            _log.debug(f"Request for issue list '{list_name}' hit cache.")
            return issues
        # Otherwise get the issues from Jira
        issues = []
        path = f'/rest/api/3/search?&fields=issuetype,status,priority,summary,created,duedate,resolutiondate,customfield_10058,customfield_10067,customfield_10069&jql=filter%3D{filter_id}'
        js = self.request(path)
        js_issues = js['issues']
        _log.info(f"Get issues '{list_name}' (id: {filter_id}) ...")
        for js_issue in js_issues:
            issue = Issue.from_jira_js(js_issue)
            issues.append(issue)
            _log.debug(f'Got issue {issue}')
        # Update cache
        if self.cache is not None:
            self.cache.update_data('issue_lists', list_name, issues)
        return issues


    class Error(GeneralError):

        TOPIC = 'Jira API'


class IssueCache(object):

    def __init__(self):
        self.max_age = 3600
        self.data = {}

    def get_data(self, category, key, max_age=None):
        max_age = max_age if max_age is not None else self.max_age
        cat_data = self.data.get(category, None)
        if cat_data is None:
            return None
        d = cat_data.get(key, None)
        if d is None:
            return None
        if time.time() - d.timestamp > max_age:
            del cat_data[key]
            return None
        return d.data

    def update_data(self, category, key, data):
        cat_data = self.data.get(category, None)
        if cat_data is None:
            cat_data = {}
            self.data[category] = cat_data
        cat_data[key] = self.Data(data)

    
    class Data(object):

        def __init__(self, data):
            self.data = data
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
        jira.set_cache(issue_cache)
        if user is not None and token is not None:
            jira.set_auth(user, token)
        return jira
    config.add_request_method(jira_factory, 'jira', reify=True)