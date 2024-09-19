import logging
import os
import json

from datetime import date
from urllib.parse import urlparse

from triweb.errors import GeneralError

_log = logging.getLogger(__name__)


class Document(object):

    def __init__(self, content, version=0):
        self.version = version
        self.content = content

    @classmethod
    def load(cls, doc):
        if 'type' not in doc or doc['type'] != 'doc':
            raise Document.Error('Unbekannter Dokumenttyp!')
        if 'content' not in doc:
            raise Document.Error('Leeres Dokument!')
        if 'version' in doc:
            return Document(doc['content'], doc['version'])
        return Document(doc['content'])

    @classmethod
    def read(cls, s):
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
        return doc_writer.write(self.content)


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

        def __init__(self, header_offset=0, issue_id=None):
            self.html = ''
            self.header_offset = header_offset
            self.issue_id = issue_id

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

        def write_paragraph(self, attrs, content):
            self.html += '<p>'
            self._write(content)
            self.html += '</p>\n'

        def write_date(self, attrs, content):
            try:
                ts = int(attrs.get('timestamp')) / 1000
            except:
                ts = 0
            d = date.fromtimestamp(ts)
            self.html += f'<span convert="to_date">{d}</span>'

        def write_heading(self, attrs, content):
            level = attrs.get('level', 6) + self.header_offset
            self.html += f'<h{level}>'
            self._write(content)
            self.html += f'</h{level}>\n'

        def write_mention(self, attrs, content):
            user = attrs.get('text')
            if user.startswith('@'):
                user = user[1:]
            self.html += f'<span class="text-nowrap">{user}</span>'

        def write_issue_link(self, attrs, content):
            jira_url = urlparse(attrs.get('url'))
            issue_key = os.path.basename(jira_url.path)
            if len(issue_key) > 0:
                url = f'/issue/{issue_key}'
            else:
                issue_key = '<em>ungültige Referenz</em>'
                url = '#'
            self.html += f'<a href="{url}">{issue_key}</a>'

        def write_bullet_list(self, attrs, content):
            self.html += '<ul>\n'
            self._write(content)
            self.html += '</ul>\n'

        def write_ordered_list(self, attrs, content):
            start = attrs.get('order', 1)
            self.html += f'<ol start="{start}">\n'
            self._write(content)
            self.html += '</ol>\n'

        def write_list_item(self, attrs, content):
            self.html += '<li>\n'
            self._write(content)
            self.html += '</li>\n'

        def write_single_media(self, attrs, content):
            width = attrs.get('width', 66.6)
            side = round((100 - width) * 6 / 100)
            middle = 12 - side * 2
            self.html += '<div class="row mb-4">\n' \
                    f'<div class="col-{side}"></div>\n' \
                    f'<div class="col-{middle}">\n'
            self._write(content)
            self.html += '</div>\n' \
                    f'<div class="col-{side}"></div>\n' \
                    '</div>\n'

        def write_media(self, attrs, content):
            media_id = attrs.get('id', 'unknown-id')
            alt = attrs.get('alt', 'unknown ')
            src = '/rest/attachment'
            if self.issue_id is not None:
                src += f'/{self.issue_id}'
            src += f'/{media_id}'
            self.html += f'<img class="img-fluid" src="{src}" alt="{alt}" />'

        def write_table_cell(self, attrs, content, header=False):
            cell_type = 'h' if header else 'd'
            self.html += f'<t{cell_type}>\n'
            self._write(content)
            self.html += f'</t{cell_type}>\n'

        def _write_table_row(self, row):
            if row.get('type') != 'tableRow':
                _log.error(f"Element type '{row.get('type')}' != 'tableRow'!")
            self.html += '<tr>\n'
            row_content = row.get('content', [])
            self._write(row_content)
            self.html += '</tr>\n'

        def _write_table_rows(self, rows):
            for row in rows:
                self._write_table_row(row)

        def _write_table_header(self, row):
            self.html += '<thead>\n'
            self._write_table_row(row)
            self.html += '</thead>\n'

        def _write_table_body(self, rows):
            self.html += '<tbody class="table-group-divider">\n'
            self._write_table_rows(rows)
            self.html += '</tbody>\n'

        def write_table(self, attrs, content):
            self.html += '<table class="table mb-4">\n'
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
                self._write_table_header(first_row)
                self._write_table_body(content[1:])
            else:
                # ... without header
                self._write_table_rows(content)
            self.html += '</table>\n'

        def write_panel(self, attrs, content):
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
            self._write(content)
            self.html += '</div></div>\n'

        def write_element(self, t, attrs, content):
            if t == 'paragraph':
                self.write_paragraph(attrs, content)
            elif t == 'date':
                self.write_date(attrs, content)
            elif t == 'heading':
                self.write_heading(attrs, content)
            elif t == 'mention':
                self.write_mention(attrs, content)
            elif t == 'inlineCard':
                self.write_issue_link(attrs, content)
            elif t == 'bulletList':
                self.write_bullet_list(attrs, content)
            elif t == 'orderedList':
                self.write_ordered_list(attrs, content)
            elif t == 'listItem':
                self.write_list_item(attrs, content)
            elif t == 'mediaSingle':
                self.write_single_media(attrs, content)
            elif t == 'media':
                self.write_media(attrs, content)
            elif t == 'tableHeader':
                self.write_table_cell(attrs, content, header=True)
            elif t == 'tableCell':
                self.write_table_cell(attrs, content)
            elif t == 'table':
                self.write_table(attrs, content)
            elif t == 'panel':
                self.write_panel(attrs, content)
            else:
                _log.error(f"Unknown element type '{t}'!")

        def mark_text_link(self, attrs, text):
            href = attrs.get('href')
            if href is None:
                return text
            return f'<a href="{href}" target="blank">{text}</a>'

        def mark_text(self, t, attrs, text):
            if t == 'link':
                text = self.mark_text_link(attrs, text)
            elif t == 'strong':
                text = f'<strong>{text}</strong>'
            else:
                _log.error(f"Unknown text mark type '{t}'!")
            return text

        def _write(self, content):
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
                    self.write_element(t, attrs, content)
            return self.html

        def write(self, content):
            self.write_styles()
            return self._write(content)


    class Error(GeneralError):

        TOPIC = 'Atlassian Document Format'


### TEST PROGRAM  ###
if __name__ == "__main__":

    import sys

    logging.getLogger().setLevel(logging.DEBUG)
    logging.info('Test Atlassian Document Format (ADF) Parser')

    if len(sys.argv) < 2:
        _log.error('Usage: adf.py FILE')
        exit(1)

    adf_data = open(sys.argv[1]).read()

    doc = Document.read(adf_data)
    html = doc.write()

    print('=== HTML ===')
    print(html)
