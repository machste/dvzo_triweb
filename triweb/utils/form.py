import re

from copy import deepcopy
from datetime import date, time

from triweb.errors import GeneralError


class Form(object):

    def __init__(self, name, field_names=None):
        self.name = name
        self.fields = []
        if field_names is not None:
            for name in field_names:
                self.add_field(self.Field(name))
        self.validated = False
        self.valid = False

    def __getattr__(self, name):
        for field in self.fields:
            if field.name == name:
                return field
        raise AttributeError()

    def add_field(self, field):
        field.form = self
        # Set copy and validator functions
        if field.copy_from_cb is None:
             field.copy_from_cb = getattr(self, f'do_copy_{field.name}_from', None)
        if field.copy_to_cb is None:
            field.copy_to_cb = getattr(self, f'do_copy_{field.name}_to', None)
        if field.validator is None:
            field.validator = getattr(self, f'do_validate_{field.name}', None)
        self.fields.append(field)

    def copy_from(self, model, **kw):
        for field in self.fields:
            field.do_copy_from(model, **kw)

    def copy_to(self, model, **kw):
        for field in self.fields:
            if field.ignore:
                continue
            field.do_copy_to(model, **kw)

    def validate_each(self, params, **kw):
        self.valid = True
        for field in self.fields:
            field.get_from_params(params)
            try:
                field.do_validation(**kw)
            except Form.Field.Reset:
                field.reset()
            except Form.Field.Ignore:
                field.ignore = True
                continue
            except Form.Field.MissingValidator:
                yield field
            field.validated = True
            if not field.is_valid():
                self.valid = False
        self.validated = True

    def validate(self, params, **kw):
        for field in self.validate_each(params, **kw):
            field.err_msg = 'Dieses Eingabefeld ist ungültig!'
        return self.is_valid()

    def reset(self):
        for field in self.fields:
            field.reset()
        self.validated = False
        self.valid = False

    def is_valid(self):
        return self.validated and self.valid

    def __repr__(self):
        return f'{self.name}: {self.fields}'


    class Error(GeneralError):

        TOPIC = "Formular Fehler"


    class Field(object):

        TYPE = 'custom'
        DEFAULT = ''
        EMAIL_REGEX = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}'

        def __init__(self, name, validator=None):
            self.name = name
            self.copy_from_cb = None
            self.copy_to_cb = None
            self.validator = validator
            self.form = None
            self.reset()

        def reset(self):
            self.value = deepcopy(self.DEFAULT)
            self.ignore = False
            self.err_msg = ''
            self.validated = False

        def is_email(self):
            return re.fullmatch(self.EMAIL_REGEX, self.value)

        def is_validated(self):
            return not self.ignore and self.validated

        def is_valid(self):
            return self.err_msg is None or len(self.err_msg) == 0

        def get_from_params(self, params):
            self.value = params.get(self.name, self.DEFAULT)

        def copy_from(self, model, **kw):
            val = getattr(model, self.name)
            if val is not None:
                self.value = val

        def do_copy_from(self, model, **kw):
            if self.copy_from_cb is None:
                self.copy_from(model, **kw)
            else:
                self.copy_from_cb(self, model, **kw)

        def copy_to(self, model, **kw):
            setattr(model, self.name, self.value)

        def do_copy_to(self, model, **kw):
            if self.copy_to_cb is None:
                self.copy_to(model, **kw)
            else:
                self.copy_to_cb(self, model, **kw)

        def convert(self):
            pass

        def validate(self):
            raise Form.Field.MissingValidator()

        def do_validation(self, **kw):
            self.convert()
            if self.validator is None:
                self.validate(*kw)
            elif self.validator != False:
                try:
                    self.validator(self, **kw)
                except Form.Field.Error as err:
                    self.err_msg = err.msg
            self.validated = True

        def get_valid_cls(self):
            if not self.is_validated():
                return None
            if self.is_valid():
                return "is-valid"
            else:
                return "is-invalid"

        def __repr__(self):
            return f'({self.name}, {self.value}, {self.err_msg})'

        class Reset(Exception):
            pass

        class Ignore(Exception):
            pass

        class MissingValidator(Exception):
            pass

        class Error(Exception):

            def __init__(self, msg):
                self.msg = msg


    class TextField(Field):

        TYPE = 'text'

        def __init__(self, name, validator=None, allow_empty=False):
            super().__init__(name, validator)
            self.allow_empty = allow_empty

        def copy_to(self, model, **kw):
            val = None if len(self.value) == 0 else self.value
            setattr(model, self.name, val)

        def convert(self):
            if self.value is None:
                self.value = ''
            else:
                self.value = str(self.value).strip()

        def validate(self, **kw):
            if len(self.value) > 0 or self.allow_empty:
                return
            self.err_msg = 'Dieses Feld darf nicht leer sein!'


    class DateField(Field):

        TYPE = 'date'

        def __init__(self, name, validator=None, allow_empty=False,
                allow_past=True):
            super().__init__(name, validator)
            self.allow_empty = allow_empty
            self.allow_past = allow_past

        @property
        def date(self):
            try:
                return date.fromisoformat(self.value)
            except ValueError:
                return None

        @date.setter
        def date(self, d):
            self.value = d.isoformat() if d is not None else None

        def copy_from(self, model, **kw):
            self.date = getattr(model, self.name)

        def copy_to(self, model, **kw):
            setattr(model, self.name, self.date)

        def validate(self, **kw):
            if self.date is None:
                if self.allow_empty:
                    raise Form.Field.Ignore()
                self.err_msg = 'Bitte wähle ein gültiges Datum!'
            elif not self.allow_past and self.date < date.today():
                self.err_msg = 'Datum liegt in der Vergangenheit!'


    class TimeField(Field):

        TYPE = 'time'

        @property
        def time(self):
            return time.fromisoformat(self.value)

        @time.setter
        def time(self, t):
            self.value = t.isoformat() if t is not None else None

        def copy_from(self, model, **kw):
            self.time = getattr(model, self.name)

        def copy_to(self, model, **kw):
            setattr(model, self.name, self.time)

        def validate(self, **kw):
            pass


    class Checkbox(Field):

        TYPE = 'checkbox'
        DEFAULT = False

        def get_from_params(self, params):
            self.value = self.name in params

        def validate(self, **kw):
            pass


    class ColorField(Field):

        TYPE = 'color'
        COLOR_REGEX = r'#(?:[a-fA-F0-9]{2}){3,4}'

        def is_color(self):
            return re.fullmatch(self.COLOR_REGEX, self.value)

        def validate(self, **kw):
            if not self.is_color():
                self.err_msg = 'Bitte wähle einen gültigen Farbwert!'


    class Select(Field):

        TYPE = 'text'

        def __init__(self, name, options, validator=None):
            super().__init__(name, validator=validator)
            self.options = options

        def validate(self, **kw):
            pass


    class SelectId(Select):

        TYPE = 'id'

        def convert(self):
            try:
                self.value = int(self.value)
            except:
                self.err_msg = f'Ungültige Auswahl!'


    class SelectMultiple(SelectId):

        TYPE = 'select_multiple'
        DEFAULT = []

        def __init__(self, name, options, validator=None, allow_empty=False):
            super().__init__(name, options, validator=validator)
            self.allow_empty = allow_empty

        @property
        def values(self):
            return self.value

        def get_from_params(self, params):
            self.value = params.getall(self.name)


    class SelectMultipleIds(SelectMultiple):

        TYPE = 'select_ids'

        @property
        def ids(self):
            return self.value

        def get_from_params(self, params):
            self.value = params.getall(self.name)

        def copy_from(self, model, **kw):
            collection = getattr(model, self.name, [])
            for item in collection:
                self.ids.append(item.id)

        def copy_to(self, model, **kw):
            collection = getattr(model, self.name, [])
            collection.clear()
            for id in self.ids:
                for option in self.options:
                    if option.id != id:
                        continue
                    collection.append(option)
                    break

        def convert(self):
            ids = []
            for id in self.value:
                try:
                    ids.append(int(id))
                except Exception:
                    self.err_msg = f"Ungültige ID '{id}' in der Liste!"
            self.value = ids

        def validate(self, **kw):
            if not self.allow_empty and len(self.value) == 0:
                self.err_msg = f'Bitte selektiere mindestens ein Element!'
