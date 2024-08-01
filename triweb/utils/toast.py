from enum import Enum


class TypeMember(object):

    def __init__(self, name, icon_name=None, icon_color=None):
        self.name = name
        self.icon_name = icon_name
        self.icon_color = icon_color

    def __repr__(self):
        return str(self.name)


class Toast(object):

    class Type(Enum):
        DEFAULT = TypeMember('default')
        INFO = TypeMember('info', 'info-circle-fill')
        SUCCESS = TypeMember('success', 'check-circle-fill', 'success')
        WARNING = TypeMember('warning', 'exclamation-circle-fill', 'warning')
        DANGER = TypeMember('danger', 'exclamation-triangle-fill', 'danger')

    def __init__(self, message, title=None, type=Type.DEFAULT):
        self.message = message
        self.title = title or ''
        if isinstance(type, Toast.Type):
            self.type = type
        else:
            self.type = Toast.Type.DEFAULT
            for member in Toast.Type:
                if member.name == type:
                    self.type = member
                    break

    def has_icon(self):
        return self.type.value.icon_name is not None

    @property
    def icon(self):
        icon = ''
        if self.has_icon():
            icon = f'<i class="bi bi-{self.type.value.icon_name}'
            if self.type.value.icon_color is not None:
                icon += f' text-{self.type.value.icon_color}'
            icon += '"></i>'
        return icon
