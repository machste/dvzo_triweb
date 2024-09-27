import re


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
        if field.validator is None:
            field.validator = getattr(self, f'do_validate_{field.name}', None)
        self.fields.append(field)

    def copy_from(self, model):
        for field in self.fields:
            new_value = getattr(model, field.name, None)
            if new_value is not None:
                field.value = new_value

    def copy_to(self, model):
        pass

    def validate_each(self, params, **kw):
        self.valid = True
        for field in self.fields:
            field.get_from_params(params)
            try:
                field.validate(**kw)
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


    class Field(object):

        TYPE = 'custom'
        DEFAULT = ''
        EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

        def __init__(self, name, validator=None):
            self.name = name
            self.validator = validator
            self.form = None
            self.reset()

        def reset(self):
            self.value = self.DEFAULT
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

        def validate(self, **kw):
            if self.validator == False:
                raise Form.Field.Ignore()
            if self.validator is None:
                raise Form.Field.NoValidator()
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
            if self.validator == False:
                raise Form.Field.Ignore()
            if self.value is None or len(self.value) == 0:
                if self.allow_empty:
                    raise Form.Field.Ignore()
                self.err_msg = 'Dieses Feld darf nicht leer sein!'
            elif self.validator is not None:
                try:
                    self.validator(self, **kw)
                except Form.Field.Error as err:
                    self.err_msg = err.msg
            self.validated = True

    class SelectMultiple(Field):

        TYPE = 'select_multiple'
        DEFAULT = []

        def __init__(self, name, validator=None):
            super().__init__(name, validator)

        def get_from_params(self, params):
            self.value = params.getall(self.name)
