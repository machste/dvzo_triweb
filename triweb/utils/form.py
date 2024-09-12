import re

from copy import deepcopy

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
            except Form.Field.Ignore:
                field.ignore = True
                continue
            except Form.Field.NoValidator:
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
            new_value = getattr(model, self.name, None)
            if new_value is not None:
                self.value = new_value

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
            raise Form.Field.NoValidator()

        def do_validation(self, **kw):
            self.convert()
            if self.validator == False:
                raise Form.Field.Ignore()
            if self.validator is None:
                self.validate(*kw)
            else:
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


        class NoValidator(Exception):
            pass

        class Ignore(Exception):
            pass

        class Error(Exception):

            def __init__(self, msg):
                self.msg = msg


    class TextField(Field):

        TYPE = 'text'

        def __init__(self, name, allow_empty=False):
            super().__init__(name)
            self.allow_empty = allow_empty

        def validate(self, **kw):
            if self.value is None or len(self.value) == 0:
                if self.allow_empty:
                    raise Form.Field.Ignore()
                self.err_msg = 'Dieses Feld darf nicht leer sein!'


    class ColorField(Field):

        TYPE = 'color'
        COLOR_REGEX = r'#(?:[a-fA-F0-9]{2}){3,4}'

        def is_color(self):
            return re.fullmatch(self.COLOR_REGEX, self.value)

        def validate(self, **kw):
            if not self.is_color():
                self.err_msg = 'Bitte wähle einen gültigen Farbwert!'


    class SelectId(Field):

        TYPE = 'id'

        def __init__(self, name, options, validator=None, allow_empty=False):
            super().__init__(name, validator=validator)
            self.options = options
            self.allow_empty = allow_empty

        def convert(self):
            try:
                self.value = int(self.value)
            except:
                self.err_msg = f'Ungültige Auswahl!'

        def validate(self, **kw):
            pass

    class SelectMultiple(SelectId):

        TYPE = 'select_multiple'
        DEFAULT = []

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
