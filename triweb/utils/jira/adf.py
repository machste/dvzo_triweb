import logging
import os
import json

from datetime import date, datetime
from urllib.parse import urlparse

from triweb.errors import GeneralError

_log = logging.getLogger(__name__)


class Document(object):

    def __init__(self, content=None, version=1):
        self.version = version
        self.adf_content = None
        self.content = []
        if content is not None:
            self.add_content(content)
        self.attachments = []

    @classmethod
    def load(cls, adf_data):
        # Check ADF type
        if 'type' not in adf_data or adf_data['type'] != 'doc':
            raise Document.Error('Unbekannter Dokumenttyp!')
        # Check ADF version
        if 'version' in adf_data:
            doc = Document(version=adf_data['version'])
        else:
            doc = Document()
        # Check and add content
        if 'content' not in adf_data:
            raise Document.Error('Leeres Dokument!')
        doc.adf_content = adf_data['content']
        return doc

    def dump_content(self):
        if self.adf_content is not None:
            return self.adf_content
        elif self.content is not None:
            content = []
            for c in self.content:
                content.append(c.dump())
        return content

    def dump(self):
        js = dict(type='doc', version=self.version)
        js['content'] = self.dump_content()
        return js

    @classmethod
    def read(cls, s, format='adf', **kw):
        doc_reader = None
        if format == 'plain':
            doc_reader = Document.Plain(**kw)
        if doc_reader is not None:
            return doc_reader.read(s)
        try:
            doc = json.loads(s)
        except:
            raise Document.Error('Ungültige ADF Daten!')
        return cls.load(doc)

    def write(self, format='html', **kw):
        if format == 'html':
            doc_writer = Document.Html(**kw)
        else:
            raise Document.Error(f"Ungültiges Ausgabeformat '{format}'!")
        return doc_writer.write(self)

    def add_content(self, content):
        if isinstance(content, str):
            content = Document.Paragraph(content)
        elif not isinstance(content, Document.Content):
            raise Document.Error(f'Ungültiger ADF Inhalt!')
        self.content.append(content)

    def add_attachment(self, attachment):
        self.attachments.append(attachment)

    def get_attachment(self, id):
        for att in self.attachments:
            if att.id == id or att.media_id == id:
                return att
        return None


    class Content(object):

        def __init__(self, type):
            self.type = type
            self.empty_content = False
            self.convert_strings = False
            self.attrs = None
            self.content = []

        def handle_unknown_content(self, content):
            _log.error(f'Invalid ADF content! ({content})')
            raise Document.Error('Ungültiger ADF Inhalt!')

        def add_content(self, content):
            if isinstance(content, Document.Content):
                self.content.append(content)
            elif isinstance(content, list):
                for c in content:
                    self.add_content(c)
            elif isinstance(content, str) and self.convert_strings:
                self.content.append(Document.Text(content))
            else:
                self.handle_unknown_content(content)

        def dump(self):
            js = dict(type=self.type)
            if self.attrs is not None:
                js['attrs'] = self.attrs
            if len(self.content) > 0 or self.empty_content:
                js['content'] = []
                for c in self.content:
                    js['content'].append(c.dump())
            return js

    class Text(Content):

        def __init__(self, text):
            super().__init__('text')
            self.text = str(text)

        def dump(self):
            js = super().dump()
            js['text'] = self.text
            return js


    class Paragraph(Content):

        def __init__(self, content=None):
            super().__init__('paragraph')
            self.convert_strings = True
            if content is not None:
                self.add_content(content)

    class Heading(Content):

        def __init__(self, level, text):
            super().__init__('heading')
            self.convert_strings = True
            try:
                level = int(level)
            except:
                _log.warn(f"Invalid value '{level}' for heading level!")
                level = 0
            self.attrs = dict(level=level)
            self.add_content(text)


    class Date(Content):

        def __init__(self, d):
            super().__init__('date')
            self.set_date(d)

        def set_date(self, d):
            if isinstance(d, str):
                timestamp = int(datetime.fromisoformat(d).timestamp())
            elif isinstance(d, int):
                timestamp = d
            elif isinstance(d, float):
                timestamp = int(d)
            elif isinstance(datetime, d):
                timestamp = int(d.timestamp())
            elif isinstance(date, d):
                timestamp = int(datetime(d.day, d.month, d.day).timestamp())
            else:
                timestamp = 0
            self.attrs = dict(timestamp=str(timestamp * 1000))



    class Html(object):

        DEF_CSS = {
            'table p': {
                'margin-top': '0 !important',
                'margin-bottom': '0 !important'
            },
            'table th strong': {
                'font-weight': 'inherit'
            },
            'table .alert': {
                'padding': '0 0.5rem',
                'margin-bottom': '0'
            },
            'table .alert .bi': {
                'font-size': '1rem',
                'margin-right': '0.5rem'
            },
            '.alert .bi': {
                'font-size': '1.75rem',
                'margin-right': '1rem'
            },
            '.alert p': {
                'margin-top': '0.25rem',
                'margin-bottom': '0.25rem'
            }
        }

        def __init__(self, header_offset=0):
            self.html = ''
            self.header_offset = header_offset

        def write_styles(self):
            if len(self.DEF_CSS) == 0:
                return
            self.html += '<style>\n'
            for selector, props in self.DEF_CSS.items():
                self.html += f'{selector} {{\n'
                for key, value in props.items():
                    self.html += f'\t{key}: {value};'
                self.html += '}\n'
            self.html += '</style>\n'

        def write_paragraph(self, doc, attrs, content):
            self.html += '<p>'
            self._write(doc, content)
            self.html += '</p>\n'

        def write_date(self, doc, attrs, content):
            try:
                ts = int(attrs.get('timestamp')) / 1000
            except:
                ts = 0
            d = date.fromtimestamp(ts)
            self.html += f'<span convert="to_date">{d}</span>'

        def write_heading(self, doc, attrs, content):
            level = attrs.get('level', 6) + self.header_offset
            self.html += f'<h{level}>'
            self._write(doc, content)
            self.html += f'</h{level}>\n'

        def write_mention(self, doc, attrs, content):
            user = attrs.get('text')
            if user.startswith('@'):
                user = user[1:]
            self.html += f'<span class="text-nowrap">{user}</span>'

        def write_issue_link(self, doc, attrs, content):
            jira_url = urlparse(attrs.get('url'))
            issue_key = os.path.basename(jira_url.path)
            if len(issue_key) > 0:
                url = f'/issue/{issue_key}'
            else:
                issue_key = '<em>ungültige Referenz</em>'
                url = '#'
            self.html += f'<a href="{url}">{issue_key}</a>'

        def write_bullet_list(self, doc, attrs, content):
            self.html += '<ul>\n'
            self._write(doc, content)
            self.html += '</ul>\n'

        def write_ordered_list(self, doc, attrs, content):
            start = attrs.get('order', 1)
            self.html += f'<ol start="{start}">\n'
            self._write(doc, content)
            self.html += '</ol>\n'

        def write_list_item(self, doc, attrs, content):
            self.html += '<li>\n'
            self._write(doc, content)
            self.html += '</li>\n'

        def write_single_media(self, doc, attrs, content):
            width = attrs.get('width', 66.6)
            side = round((100 - width) * 6 / 100)
            middle = 12 - side * 2
            self.html += '<div class="row mb-4">\n' \
                    f'<div class="col-{side}"></div>\n' \
                    f'<div class="col-{middle}">\n'
            self._write(doc, content)
            self.html += '</div>\n' \
                    f'<div class="col-{side}"></div>\n' \
                    '</div>\n'

        def write_media(self, doc, attrs, content):
            media_id = attrs.get('id', 'unknown-id')
            alt = attrs.get('alt', 'unknown')
            src = f'/rest/attachment/{media_id}'
            media_type = "image/png"
            att = doc.get_attachment(media_id)
            if att is not None:
                media_type = att.content_type
            if media_type.startswith('video'):
                self.html += '<video class="img-fluid" controls>\n' \
                        f'<source src="{src}" type="{media_type}">\n' \
                        'Dieser Browser unterstützt keine Videos.\n' \
                        '</video>'
            else:
                self.html += f'<img class="img-fluid" src="{src}" alt="{alt}" />'

        def write_table_cell(self, doc, attrs, content, header=False):
            cell_type = 'h' if header else 'd'
            colspan = attrs.get('colspan')
            self.html += f'<t{cell_type}'
            if colspan is not None:
                self.html += f' colspan="{colspan}"'
            self.html += '>\n'
            self._write(doc, content)
            self.html += f'</t{cell_type}>\n'

        def _write_table_row(self, doc, row):
            if row.get('type') != 'tableRow':
                _log.error(f"Element type '{row.get('type')}' != 'tableRow'!")
            self.html += '<tr>\n'
            row_content = row.get('content', [])
            self._write(doc, row_content)
            self.html += '</tr>\n'

        def _write_table_rows(self, doc, rows):
            for row in rows:
                self._write_table_row(doc, row)

        def _write_table_header(self, doc, row):
            self.html += '<thead>\n'
            self._write_table_row(doc, row)
            self.html += '</thead>\n'

        def _write_table_body(self, doc, rows):
            self.html += '<tbody class="table-group-divider">\n'
            self._write_table_rows(doc, rows)
            self.html += '</tbody>\n'

        def write_table(self, doc, attrs, content):
            self.html += '<div class="table-responsive">\n' \
                    '<table class="table mb-4">\n'
            first_row = None
            header = False
            # Get first row of the table ...
            if len(content) > 0 and content[0].get('type') == 'tableRow':
                first_row = content[0]
                c = first_row.get('content', [])
                # ... and check whether it is a header row
                header = len(c) > 0 and c[0].get('type') == 'tableHeader'
            # Write table ...
            if header:
                # ... with header
                self._write_table_header(doc, first_row)
                self._write_table_body(doc, content[1:])
            else:
                # ... without header
                self._write_table_rows(doc, content)
            self.html += '</table>\n</div>\n'

        def write_panel(self, doc, attrs, content):
            panel_type = attrs.get('panelType')
            alert_type = 'primary'
            alert_icon = 'info-circle-fill'
            if panel_type == 'error':
                alert_type = 'danger'
                alert_icon = 'x-circle-fill'
            elif panel_type == 'warning':
                alert_type = 'warning'
                alert_icon = 'exclamation-triangle-fill'
            elif panel_type == 'success':
                alert_type = 'success'
                alert_icon = 'check-circle-fill'
            elif panel_type == 'note':
                alert_type = 'info'
                alert_icon = 'sticky-fill'
            self.html += f'<div class="alert alert-{alert_type} d-flex align-items-center" role="alert">' \
                         f'<i class="bi bi-{alert_icon}"></i><div>\n'
            self._write(doc, content)
            self.html += '</div></div>\n'

        def write_status(self, doc, attrs, content):
            text = attrs.get('text', ' ')
            color = attrs.get('color')
            color_to_badge_type = {
                'grey': 'secondary', 'purple': 'info', 'blue': 'primary',
                'red': 'danger', 'yellow': 'warning', 'green': 'success'
            }
            badge_type = color_to_badge_type.get(color, 'secondary')
            self.html += f'<span class="badge text-bg-{badge_type}">{text}</span>\n'

        def write_blockquote(self, doc, attrs, content):
            self.html += '<div class="ps-3 border-start border-5"><em>\n'
            self._write(doc, content)
            self.html += '</em></div>\n'

        def write_hard_break(self, doc, attrs, content):
            self.html += '<br \>'

        def write_element(self, t, doc, attrs, content):
            if t == 'paragraph':
                self.write_paragraph(doc, attrs, content)
            elif t == 'date':
                self.write_date(doc, attrs, content)
            elif t == 'heading':
                self.write_heading(doc, attrs, content)
            elif t == 'mention':
                self.write_mention(doc, attrs, content)
            elif t == 'inlineCard':
                self.write_issue_link(doc, attrs, content)
            elif t == 'bulletList':
                self.write_bullet_list(doc, attrs, content)
            elif t == 'orderedList':
                self.write_ordered_list(doc, attrs, content)
            elif t == 'listItem':
                self.write_list_item(doc, attrs, content)
            elif t == 'mediaSingle':
                self.write_single_media(doc, attrs, content)
            elif t == 'media':
                self.write_media(doc, attrs, content)
            elif t == 'tableHeader':
                self.write_table_cell(doc, attrs, content, header=True)
            elif t == 'tableCell':
                self.write_table_cell(doc, attrs, content)
            elif t == 'table':
                self.write_table(doc, attrs, content)
            elif t == 'panel':
                self.write_panel(doc, attrs, content)
            elif t == 'status':
                self.write_status(doc, attrs, content)
            elif t == 'blockquote':
                self.write_blockquote(doc, attrs, content)
            elif t == 'hardBreak':
                self.write_hard_break(doc, attrs, content)
            else:
                _log.error(f"Unknown element type '{t}'!")

        def mark_text_link(self, attrs, text):
            href = attrs.get('href')
            if href is None:
                return text
            return f'<a href="{href}" target="blank">{text}</a>'

        def mark_text_subsup(self, attrs, text):
            t = attrs.get('type')
            if t not in ('sub', 'sup'):
                t = 'span'
            return f'<{t}>{text}</{t}>'

        def mark_text(self, t, attrs, text):
            if t == 'link':
                text = self.mark_text_link(attrs, text)
            elif t == 'strong':
                text = f'<strong>{text}</strong>'
            elif t == 'em':
                text = f'<em>{text}</em>'
            elif t == 'subsup':
                text = self.mark_text_subsup(attrs, text)
            else:
                _log.error(f"Unknown text mark type '{t}'!")
            return text

        def _write(self, doc, content):
            for el in content:
                if 'type' not in el:
                    _log.error('No type defined for document element!')
                    continue
                # Get element type
                t = el['type']
                if t == 'text':
                    # Handle text elements here
                    text = el.get('text')
                    marks = el.get('marks', [])
                    for mark in marks:
                        if 'type' not in mark:
                            _log.error('No type defined for text mark!')
                            continue
                        attrs = mark.get('attrs')
                        text = self.mark_text(mark['type'], attrs, text)
                    self.html += text
                else:
                    # Handle more complex elements
                    attrs = el.get('attrs', {})
                    content = el.get('content', [])
                    self.write_element(t, doc, attrs, content)
            return self.html

        def write(self, doc):
            self.write_styles()
            return self._write(doc, doc.dump_content())


    class Plain(object):

        def read(self, s):
            doc = Document()
            doc.add_content(s)
            return doc


    class Error(GeneralError):

        TOPIC = 'Atlassian Document Format'


### TEST PROGRAM  ###
if __name__ == "__main__":

    import sys

    logging.getLogger().setLevel(logging.DEBUG)
    logging.info('Test Atlassian Document Format (ADF) Parser')

    # Parse arguments
    format = 'adf'
    if len(sys.argv) == 3:
        format = sys.argv[1]
        fname = sys.argv[2]
    elif len(sys.argv) == 2:
        fname = sys.argv[1]
    else:
        _log.error('Usage: adf.py [FORMAT] FILE')
        exit(1)
    # Read data from file
    data = open(fname).read()
    # Parse data
    doc = Document.read(data, format=format)
    # Print HTML
    print('=== HTML ===')
    print(doc.write(format='html'))
