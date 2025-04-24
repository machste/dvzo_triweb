import logging
import requests
import time

from threading import RLock
from requests.auth import HTTPBasicAuth

from triweb.utils.jira.issue import Issue
from triweb.utils.jira.attachment import Attachment
from triweb.utils.decorators import lock
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
        'tmiii.open': 10096,
        'temiii.open': 10031,
        'tmii.open': 10129,
        'em33-15.open': 10131,
        'em33-24.open': 10132,
        'general.open': 10027,
        'doing': 10023,
        'done': 10028
    }

    GLOBAL_LOCK = RLock()

    def __init__(self, url, session=None):
        self.url = url
        self.session = session or requests.sessions.Session()
        self.auth = None
        self.cache = None

    def set_auth(self, user, token):
        self.auth = HTTPBasicAuth(user, token)

    def set_cache(self, cache):
        self.cache = cache

    def clear_cache(self):
        if self.cache is None:
            return False
        return self.cache.clear()

    def _handle_response(self, res):
        if not res.ok:
            _log.error(f"Request '{res.url}' failed!")
            raise self.Error(f"Anfrage bei '{self.url}' hat fehlgeschlagen!")
        return res

    def get(self, path, headers=None, redirects=True):
        url = self.url + path
        res = self.session.request('GET', url=url, auth=self.auth,
                headers=headers, allow_redirects=redirects)
        return self._handle_response(res)

    def get_json(self, path):
        headers = { 'Accept': 'application/json' }
        res = self.get(path, headers=headers)
        return res.json()

    def post_json(self, path, data):
        url = self.url + path
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.session.request('POST', url=url, auth=self.auth,
                headers=headers, data=data)
        self._handle_response(res)
        return res.json()

    def _get_issue_from_cache(self, id_or_key, max_age=None):
        if self.cache is None:
            return None
        def compare_issue(issue):
            if not isinstance(issue, Issue):
                return False
            if issue.id == id_or_key or issue.key == id_or_key:
                _log.debug(f"Request for issue #{issue.id} hit cache.")
                return True
            return False
        return self.cache.search_category('issues', compare_issue, max_age)

    @lock(GLOBAL_LOCK)
    def get_issue(self, id_or_key, max_age=None):
        # Check the issue cache
        issue = self._get_issue_from_cache(id_or_key, max_age)
        if issue is not None:
            return issue
        # Otherwise get the issue from Jira
        path = f'/rest/api/3/issue/{id_or_key}'
        js_issue = self.get_json(path)
        issue = Issue.from_jira_js(js_issue)
        issue.ext_link = f'{self.url}/browse/{issue.key}'
        _log.debug(f'Got issue: {issue}')
        # Get meta data of attachments
        for att in issue.attachments:
            self.get_attachment(att, data=False, max_age=max_age)
        # Update cache
        if self.cache is not None:
            self.cache.update_data('issues', issue.id, issue)
        return issue

    @lock(GLOBAL_LOCK)
    def create_issue(self, issue):
        _log.debug(f'Create issue: {issue}\n{issue.to_jira_js()}')
        path = f'/rest/api/3/issue'
        res = self.post_json(path, issue.to_jira_js())
        _log.debug(f'Response: {res}')
        return res

    def _get_attachment_from_cache(self, id, max_age=None):
        if self.cache is None:
            return None
        def compare_att(att):
            if not isinstance(att, Attachment):
                return False
            if att.id == id or att.media_id == id:
                return True
            return False
        return self.cache.search_category('attachments', compare_att, max_age)

    @lock(GLOBAL_LOCK)
    def get_attachment(self, id_or_att, data=True, max_age=None):
        if isinstance(id_or_att, Attachment):
            att = id_or_att
        else:
            att = Attachment(id_or_att)
        update_cache = False
        # Check the attachment cache
        cached_att = self._get_attachment_from_cache(att.id, max_age)
        if cached_att is None:
            update_cache = True
            # Get the attachment from Jira
            path = f'/rest/api/3/attachment/content/{att.id}'
            res = self.get(path, redirects=False)
            if not res.is_redirect:
                raise self.Error(f"Die Media-ID vom Anhang #{att.id} kann nicht geladen werden!")
            att.data_url = res.headers['Location']
            _log.debug(f'Got attachment: {att}')
        else:
            att = cached_att
        if data and not att.has_data():
            update_cache = True
            # Get the acutal data from the attachment
            res = self.session.get(att.data_url)
            att.populate(res)
            _log.debug(f'Got file: {att.name} ({att.content_type})')
        # Update cache
        if update_cache:
            self.cache.update_data('attachments', att.id, att)
        else:
            _log.debug(f"Request for attachment #{att.id} hit cache.")
        return att

    @lock(GLOBAL_LOCK)
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
        path = f'/rest/api/3/search?&fields=issuetype,status,priority,summary,creator,assignee,created,duedate,resolutiondate,customfield_10058,customfield_10067,customfield_10069&jql=filter%3D{filter_id}'
        js = self.get_json(path)
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


class Cache(object):

    def __init__(self):
        self.max_age = 3600
        self.data = {}

    def clear(self):
        self.data = {}
        return True

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

    def search_category(self, category, compare_cb, max_age=None):
        max_age = max_age if max_age is not None else self.max_age
        cat_data = self.data.get(category, None)
        if cat_data is None:
            return None
        found_key, found_data = None, None
        for key, data in cat_data.items():
            if compare_cb(data.data):
                found_key, found_data = key, data
                break
        if found_key is None:
            return None
        if time.time() - found_data.timestamp > max_age:
            del cat_data[found_key]
            return None
        return found_data.data

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
    http_session = requests.sessions.Session()
    cache = Cache()
    def jira_factory(request):
        _log.debug('Create Jira API')
        jira = Jira(url, http_session)
        jira.set_cache(cache)
        if user is not None and token is not None:
            jira.set_auth(user, token)
        return jira
    config.add_request_method(jira_factory, 'jira', reify=True)