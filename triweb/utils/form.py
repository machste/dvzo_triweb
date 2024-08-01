import re


class Form(object):

    def __init__(self, name, fields):
        self.name = name
        self.fields = []
        for field in fields:
            self.fields.append(self.Field(field, form=self))
        self.validated = False
        self.valid = False

    def __getattr__(self, name):
        for field in self.fields:
            if field.name == name:
                return field
        raise AttributeError()

    def populate(self, values, default=None):
        for field in self.fields:
            new_value = getattr(values, field.name, default)
            if new_value is not None:
                field.value = new_value

    def validate_each(self, params):
        self.valid = True
        for field in self.fields:
            field.value = params.get(field.name, None)
            yield field
            if not field.is_valid():
                self.valid = False
        self.validated = True

    def reset(self):
        for field in self.fields:
            field.value = ''
        self.validated = False
        self.valid = False

    def is_valid(self):
        return self.validated and self.valid

    def __repr__(self):
        return f'{self.name}: {self.fields}'


    class Field(object):

        EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

        def __init__(self, name, form=None):
            self.name = name
            self.value = ''
            self.err_msg = ''
            self.form = form
            self.ignore = False

        def is_email(self):
            return re.fullmatch(self.EMAIL_REGEX, self.value)

        def is_validated(self):
            return not self.ignore \
                    and (self.form is not None and self.form.validated)

        def is_valid(self):
            return self.err_msg is None or len(self.err_msg) == 0

        def get_valid_cls(self):
            if not self.is_validated():
                return None
            if self.is_valid():
                return "is-valid"
            else:
                return "is-invalid"

        def __repr__(self):
            return f'({self.name}, {self.value}, {self.err_msg})'