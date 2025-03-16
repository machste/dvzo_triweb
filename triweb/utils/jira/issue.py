from enum import Enum
from datetime import date

from triweb.utils.jira.adf import Document
from triweb.utils.jira.attachment import Attachment

class EnumValue(object):

    def __init__(self, id, name, icon_name=None, badge_color=None):
        self.id = id
        self.name = name
        self.icon_name = icon_name
        self.badge_color = badge_color

    @property
    def icon(self):
        if self.icon_name is not None:
            return f'<i class="icon icon-{self.icon_name}"></i>'
        return f'<i>{self.name}</i>'

    @property
    def badge(self):
        if self.badge_color is not None:
            return f'<span class="badge text-bg-{self.badge_color}">{self.name}</span>'
        return f'<i>{self.name}</i>'

    def __json__(self, request=None):
        return dict(name=self.name, icon=self.icon)

    def __repr__(self):
        return str(self.id)


class Worker(object):

    def __init__(self, jira_name):
        self.id = None
        self.jira_name = jira_name
        self.firstname = None
        self.lastname = None

    @property
    def short_name(self):
        return self.jira_name

    def __json__(self, request=None):
        return dict(id=self.id, short_name=self.short_name)

    def __repr__(self):
        return self.short_name


class Issue(object):

    class Type(Enum):
        LACK = EnumValue(10021, 'Mangel', 'type-lack')
        CRITICAL = EnumValue(10022, 'K.O.-Kriterium', 'type-crit')
        TASK = EnumValue(10018, 'Task', 'type-task')
        KNOWHOW = EnumValue(10031, 'Ausbildung & Knowhow', 'type-edu')
        EPIC = EnumValue(10019, 'Epic', 'type-epic')
        SUB_TASK = EnumValue(10020, 'Sub-Task', 'type-sub')
        DEFAULT = TASK

    class Priority(Enum):
        HIGHEST = EnumValue(1, 'sehr hoch', 'prio-highest')
        HIGH = EnumValue(2, 'hoch', 'prio-high')
        NORMAL = EnumValue(3, 'mittel', 'prio-medium')
        LOW = EnumValue(4, 'niedrig', 'prio-low')
        LOWEST = EnumValue(5, 'sehr niedrig', 'prio-lowest')
        DEFAULT = NORMAL

    class Status(Enum):
        TO_DO = EnumValue(10029, 'To Do', badge_color='secondary')
        DOING = EnumValue(10030, 'In Bearbeitung', badge_color='primary')
        PAUSED = EnumValue(10033, 'Pausiert', badge_color='secondary')
        TESTING = EnumValue(10032, 'Wird Getestet', badge_color='info')
        DONE = EnumValue(10031, 'Fertig', badge_color='success')
        DUPLICAT = EnumValue(10044, 'Duplikat', badge_color='warning')
        DEFAULT = TO_DO

    class Difficulty(Enum):
        NOT_RATED = EnumValue(10124, 'nicht bewertet')
        EASY = EnumValue(10122, 'einfach', 'diff-low')
        MEDIUM = EnumValue(10120, 'mittel', 'diff-medium')
        HARD = EnumValue(10121, 'anspruchsvoll', 'diff-high')
        SUPERVISED = EnumValue(10123, 'betreut')
        MASTERS_ONLY = EnumValue(10119, 'sehr schwierig', 'diff-highest')
        DEFAULT = NOT_RATED

    class Engine(Enum):
        GENERAL = EnumValue(10110, 'Allgemein')
        LOK2 = EnumValue(10111, 'Ed 3/4 2 "Hinwil"')
        LOK9 = EnumValue(10112, 'BT Eb 3/5 9')
        LOK401 = EnumValue(10113, 'Ed 3/3 401 "Bauma"')
        EE33 = EnumValue(10114, 'Ee 3/3 16363')
        TEM3 = EnumValue(10115, 'Tem III 354')
        LOK4 = EnumValue(10116, 'Ed 3/3 4 "Schwyz"')
        LOK18 = EnumValue(10117, 'E 3/3 8518 "Bäretswil"')
        TM3 = EnumValue(10118, 'Tm III 9529')
        TM2 = EnumValue(10160, 'Tm II 93')
        EM33_15 = EnumValue(10159, 'Em 3/3 18815')
        EM33_24 = EnumValue(10158, 'Em 3/3 18824')
        LOK1 = EnumValue(10125, 'Ed 3/4 1')
        DEFAULT = GENERAL

    def __init__(self, id, key):
        self.id = id
        self.key = key
        self.ext_link = None
        self._type = Issue.Type.DEFAULT
        self._priority = Issue.Priority.DEFAULT
        self._status = Issue.Status.DEFAULT
        self._difficulty = Issue.Difficulty.DEFAULT
        self._engine = Issue.Engine.DEFAULT
        self._summary = '(Kein Titel)'
        self.description = None
        self.attachments = []
        self.creator = None
        self._assignee = None
        self._workers = []
        self._created = None
        self._duedate = None
        self._resolved = None

    @property
    def type(self):
        return self._type.value.name

    @property
    def type_icon(self):
        return self._type.value.icon

    @property
    def priority(self):
        return self._priority.value.name

    @property
    def priority_icon(self):
        return self._priority.value.icon

    @property
    def status(self):
        return self._status.value.name

    @property
    def status_badge(self):
        return self._status.value.badge

    @property
    def difficulty(self):
        return self._difficulty.value.name

    @property
    def engine(self):
        return self._engine.value.name

    @property
    def assignee(self):
        if self._assignee is not None:
            return self._assignee
        elif len(self._workers) > 0:
            return self._workers[0]
        return None

    @property
    def workers(self):
        if self._assignee is not None:
            return self._workers
        return self._workers[1:]

    @property
    def contributors(self):
        if self._assignee is None:
            return self._workers
        return [Worker(self._assignee), *self._workers]

    @property
    def created(self):
        return self.parse_date(self._created)

    @property
    def duedate(self):
        return self.parse_date(self._duedate)

    @property
    def resolved(self):
        return self.parse_date(self._resolved)

    @property
    def summary(self):
        try:
            return self._summary.split(' - ', 1)[1]
        except IndexError:
            return self._summary

    def has_engine(self):
        return self._engine != Issue.Engine.DEFAULT

    @staticmethod
    def parse_date(date_str):
        if date_str is None:
            return None
        if "T" in date_str:
            date_str = date_str.split('T', 1)[0]
        try:
            return date.fromisoformat(date_str)
        except:
            return None

    @staticmethod
    def from_jira_js(js):
        self = Issue(js['id'], js['key'])
        fields = js["fields"]
        if 'summary' in fields:
            self._summary = fields['summary']
        if 'issuetype' in fields:
            try:
                type_id = int(fields['issuetype']['id'])
                for member in Issue.Type:
                    if member.value.id == type_id:
                        self._type = member
                        break
            except:
                pass
        if 'priority' in fields:
            try:
                prio_id = int(fields['priority']['id'])
                for member in Issue.Priority:
                    if member.value.id == prio_id:
                        self._priority = member
                        break
            except:
                pass
        if 'status' in fields:
            try:
                status_id = int(fields['status']['id'])
                for member in Issue.Status:
                    if member.value.id == status_id:
                        self._status = member
                        break
            except:
                pass
        if 'creator' in fields:
            try:
                self.creator = fields['creator']['displayName']
            except:
                pass
        if 'assignee' in fields:
            try:
                self._assignee = fields['assignee']['displayName']
            except:
                pass
        if 'created' in fields:
            self._created = fields['created']
        if 'duedate' in fields:
            self._duedate = fields['duedate']
        if 'resolutiondate' in fields:
            self._resolved = fields['resolutiondate']
        if 'customfield_10058' in fields:
            try:
                engine_id = int(fields['customfield_10058']['id'])
                for member in Issue.Engine:
                    if member.value.id == engine_id:
                        self._engine = member
                        break
            except:
                pass
        if 'customfield_10067' in fields:
            try:
                difficulty_id = int(fields['customfield_10067']['id'])
                for member in Issue.Difficulty:
                    if member.value.id == difficulty_id:
                        self._difficulty = member
                        break
            except:
                pass
        if 'customfield_10069' in fields:
            self._workers = []
            jira_worker_names = fields['customfield_10069']
            if jira_worker_names is not None:
                worker_names = jira_worker_names.split(',')
                for worker_name in worker_names:
                    worker_name = worker_name.strip()
                    if len(worker_name) == 0:
                        continue
                    self._workers.append(Worker(worker_name))
        if 'attachment' in fields:
            attachments = fields['attachment']
            if attachments is not None:
                for a in attachments:
                    if 'id' not in a:
                        continue
                    attachment = Attachment(a['id'])
                    attachment.content_type = a.get('mimeType')
                    self.attachments.append(attachment)
        if 'description' in fields:
            description = fields['description']
            if description is not None:
                self.description = Document.load(description)
                self.description.attachments = self.attachments
        return self

    def __json__(self, request=None):
        return dict(id=self.id, key=self.key, type=self._type.value,
                priority=self._priority.value, status=self.status,
                difficulty=self._difficulty.value, engine=self.engine,
                created=self._created, duedate=self._duedate,
                resolved=self._resolved, creator=self.creator,
                contributors=self.contributors, summary=self.summary)

    def __str__(self):
        return f'{self.key}: {self._summary}'
