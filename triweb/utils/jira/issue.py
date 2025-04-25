from enum import Enum
from datetime import date

from triweb.models.vehicle import Vehicle
from triweb.utils.jira.adf import Document
from triweb.utils.jira.attachment import Attachment


class EnumValue(object):

    def __init__(self, id, name, icon_name=None, short=None, badge_color=None):
        self.id = id
        self.name = name
        self.icon_name = icon_name
        self._short_name = short
        self.badge_color = badge_color

    @property
    def icon(self):
        if self.icon_name is not None:
            return f'<i class="icon icon-{self.icon_name}"></i>'
        return f'<i>{self.name}</i>'

    @property
    def short_name(self):
        return self._short_name or self.name

    @property
    def badge(self):
        if self.badge_color is not None:
            return f'<span class="badge text-bg-{self.badge_color}">{self.name}</span>'
        return f'<i>{self.name}</i>'

    def cmp_best_effort(self, value):
        if value == self.name or value == self.icon_name:
            return True
        if self._short_name is not None and value == self._short_name:
            return True
        try:
            if int(value) == self.id:
                return True
        except:
            pass
        return False

    def __json__(self, request=None):
        return dict(name=self.name, icon=self.icon)

    def __repr__(self):
        return str(self.id)


class IssueEnum(Enum):

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.name == value or member.value.cmp_best_effort(value):
                return member
        return None


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

    class Project(IssueEnum):
        TRI = EnumValue(10006, 'DVZO Triebfahrzeuge', short='TRI')
        DRBA = EnumValue(10007, 'DVZO Remise Bauma (Alg.)', short='DRBA')
        DEFAULT = TRI

    class Type(IssueEnum):
        LACK = EnumValue(10021, 'Mangel', 'type-lack')
        CRITICAL = EnumValue(10022, 'K.O.-Kriterium', 'type-crit')
        TASK = EnumValue(10018, 'Task', 'type-task')
        KNOWHOW = EnumValue(10031, 'Ausbildung & Knowhow', 'type-edu')
        EPIC = EnumValue(10019, 'Epic', 'type-epic')
        SUB_TASK = EnumValue(10020, 'Sub-Task', 'type-sub')
        DEFAULT = TASK

    class Priority(IssueEnum):
        HIGHEST = EnumValue(1, 'sehr hoch', 'prio-highest')
        HIGH = EnumValue(2, 'hoch', 'prio-high')
        NORMAL = EnumValue(3, 'mittel', 'prio-medium')
        LOW = EnumValue(4, 'niedrig', 'prio-low')
        LOWEST = EnumValue(5, 'sehr niedrig', 'prio-lowest')
        DEFAULT = NORMAL

    class Status(IssueEnum):
        TO_DO = EnumValue(10029, 'To Do', badge_color='secondary')
        DOING = EnumValue(10030, 'In Bearbeitung', badge_color='primary')
        PAUSED = EnumValue(10033, 'Pausiert', badge_color='secondary')
        TESTING = EnumValue(10032, 'Wird Getestet', badge_color='info')
        DONE = EnumValue(10031, 'Fertig', badge_color='success')
        DUPLICAT = EnumValue(10044, 'Duplikat', badge_color='warning')
        DEFAULT = TO_DO

    class Difficulty(IssueEnum):
        NOT_RATED = EnumValue(10124, 'nicht bewertet')
        EASY = EnumValue(10122, 'einfach', 'diff-low')
        MEDIUM = EnumValue(10120, 'mittel', 'diff-medium')
        HARD = EnumValue(10121, 'anspruchsvoll', 'diff-high')
        SUPERVISED = EnumValue(10123, 'betreut')
        MASTERS_ONLY = EnumValue(10119, 'sehr schwierig', 'diff-highest')
        DEFAULT = NOT_RATED

    class Engine(IssueEnum):
        GENERAL = EnumValue(10110, 'Allgemein')
        LOK2 = EnumValue(10111, 'Ed 3/4 2 "Hinwil"', short='Lok 2')
        LOK9 = EnumValue(10112, 'BT Eb 3/5 9', short='Lok 9')
        LOK401 = EnumValue(10113, 'Ed 3/3 401 "Bauma"', short='Lok 401')
        EE33 = EnumValue(10114, 'Ee 3/3 16363', short='Ee 3/3')
        TEM3 = EnumValue(10115, 'Tem III 354')
        LOK4 = EnumValue(10116, 'Ed 3/3 4 "Schwyz"', short='Lok 4')
        LOK18 = EnumValue(10117, 'E 3/3 8518 "Bäretswil"', short='Lok 18')
        TM3 = EnumValue(10118, 'Tm III 9529')
        TM2 = EnumValue(10160, 'Tm II 93')
        EM33_15 = EnumValue(10159, 'Em 3/3 18815')
        EM33_24 = EnumValue(10158, 'Em 3/3 18824')
        LOK1 = EnumValue(10125, 'Ed 3/4 1', short='Lok 1')
        DEFAULT = GENERAL

    def __init__(self, id=None, key=None):
        self.id = id
        self.key = key
        self.ext_link = None
        self._project = Issue.Project.DEFAULT
        self._type = Issue.Type.DEFAULT
        self._priority = Issue.Priority.DEFAULT
        self._status = Issue.Status.DEFAULT
        self._difficulty = Issue.Difficulty.DEFAULT
        self._engine = Issue.Engine.DEFAULT
        self._summary = '(Kein Titel)'
        self._description = None
        self.attachments = []
        self.creator = None
        self._assignee = None
        self._workers = []
        self._created = None
        self._duedate = None
        self._resolved = None

    @property
    def project(self):
        return self._project.value.name

    @property
    def type(self):
        return self._type.value.name

    @type.setter
    def type(self, value):
        self._type = self.Type(value)

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

    @difficulty.setter
    def difficulty(self, value):
        self._difficulty = self.Difficulty(value)

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

    def _update_summary(self, summary=None):
        if summary is None:
            summary = self.summary
        if self.has_engine():
            self._summary = f'{self._engine.value.short_name} - {summary}'
        else:
            self._summary = summary

    @summary.setter
    def summary(self, value):
        self._update_summary(value)

    @property
    def engine(self):
        return self._engine.value.name

    @engine.setter
    def engine(self, value):
        if isinstance(value, Vehicle):
            loco_name = f'{value.name} {value.number}'
        else:
            loco_name = str(value)
        for member in Issue.Engine:
            if member.value.name.startswith(loco_name):
                self._engine = member
                break
        self._update_summary()

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if isinstance(value, Document):
            self._description = value
        else:
            self._description = Document.read(str(value), format='plain')

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
        if 'project' in fields:
            try:
                self._project = self.Project(fields['project']['id'])
            except:
                pass
        if 'issuetype' in fields:
            try:
                self._type = self.Type(fields['issuetype']['id'])
            except:
                pass
        if 'priority' in fields:
            try:
                self._priority = self.Priority(fields['priority']['id'])
            except:
                pass
        if 'status' in fields:
            try:
                self._status = self.Status(fields['status']['id'])
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
                engine_id = fields['customfield_10058']['id']
                self._engine = self.Engine(engine_id)
            except:
                pass
        if 'customfield_10067' in fields:
            try:
                difficulty_id = fields['customfield_10067']['id']
                self._difficulty = self.Difficulty(difficulty_id)
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

    def to_jira_js(self):
        fields = dict()
        fields['summary'] = self._summary
        fields['project'] = dict(id=str(self._project.value.id))
        fields['issuetype'] = dict(id=str(self._type.value.id))
        fields['customfield_10058'] = dict(id=str(self._engine.value.id))
        fields['customfield_10067'] = dict(id=str(self._difficulty.value.id))
        if self._description is not None:
            fields['description'] = self._description.dump()
        return dict(fields=fields)

    def __json__(self, request=None):
        return dict(id=self.id, key=self.key, type=self._type.value,
                priority=self._priority.value, status=self.status,
                difficulty=self._difficulty.value, engine=self.engine,
                created=self._created, duedate=self._duedate,
                resolved=self._resolved, creator=self.creator,
                contributors=self.contributors, summary=self.summary)

    def __str__(self):
        if self.id is None:
            return f'NEW: {self._summary}'
        return f'{self.key}: {self._summary}'
