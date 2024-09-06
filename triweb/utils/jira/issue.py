from enum import Enum
from datetime import date


class EnumValue(object):

    def __init__(self, id, name, icon_name=None):
        self.id = id
        self.name = name
        self.icon_name = icon_name

    @property
    def icon(self):
        if self.icon_name is not None:
            return f'<i class="icon icon-{self.icon_name}"></i>'
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
        KNOWHOW = EnumValue(10031, 'Ausbildung & Knowhow')
        EPIC = EnumValue(10019, 'Epic')
        SUB_TASK = EnumValue(10020, 'Sub-Task')
        DEFAULT = TASK

    class Priority(Enum):
        HIGHEST = EnumValue(1, '++', 'prio-highest')
        HIGH = EnumValue(2, '+', 'prio-high')
        NORMAL = EnumValue(3, '=', 'prio-medium')
        LOW = EnumValue(4, '-', 'prio-low')
        LOWEST = EnumValue(5, '--', 'prio-lowest')
        DEFAULT = NORMAL

    class Status(Enum):
        TO_DO = EnumValue(10029, 'To Do')
        DOING = EnumValue(10030, 'In Bearbeitung')
        PAUSED = EnumValue(10033, 'Pausiert')
        TESTING = EnumValue(10032, 'Wird Getestet')
        DONE = EnumValue(10031, 'Fertig')
        DUPLICAT = EnumValue(10044, 'Duplikat')
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
        TM3 = EnumValue(100118, 'Tm III 9529')
        DEFAULT = GENERAL

    def __init__(self, id, key):
        self.id = id
        self.key = key
        self._type = Issue.Type.DEFAULT
        self._priority = Issue.Priority.DEFAULT
        self._status = Issue.Status.DEFAULT
        self._difficulty = Issue.Difficulty.DEFAULT
        self._engine = Issue.Engine.DEFAULT
        self._summary = '(Kein Titel)'
        self.workers = []
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
    def difficulty(self):
        return self._difficulty.value.name

    @property
    def engine(self):
        return self._engine.value.name

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
            self.workers = []
            jira_worker_names = fields.get('customfield_10069')
            if jira_worker_names is not None:
                worker_names = jira_worker_names.split(',')
                for worker_name in worker_names:
                    worker_name = worker_name.strip()
                    if len(worker_name) == 0:
                        continue
                    self.workers.append(Worker(worker_name))
        return self

    def __json__(self, request=None):
        return dict(id=self.id, key=self.key, type=self._type.value,
                priority=self._priority.value, status=self.status,
                difficulty=self._difficulty.value, engine=self.engine,
                created=self._created, duedate=self._duedate,
                resolved=self._resolved, workers=self.workers,
                summary=self.summary)

    def __str__(self):
        return f'{self.key}: {self._summary}'