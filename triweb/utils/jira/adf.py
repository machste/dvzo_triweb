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

        def __init__(self, header_offset=0, issue_id=None):
            self.html = ''
            self.header_offset = header_offset
            self.issue_id = issue_id

        def write_paragraph(self, attrs, content):
            self.html += '<p>'
            self.write(content)
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
            self.write(content)
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
            self.write(content)
            self.html += '</ul>\n'

        def write_ordered_list(self, attrs, content):
            start = attrs.get('order', 1)
            self.html += f'<ol start="{start}">\n'
            self.write(content)
            self.html += '</ol>\n'

        def write_list_item(self, attrs, content):
            self.html += '<li>\n'
            self.write(content)
            self.html += '</li>\n'

        def write_single_media(self, attrs, content):
            width = attrs.get('width', 66.6)
            side = round((100 - width) * 6 / 100)
            middle = 12 - side * 2
            self.html += '<div class="row mb-4">\n' \
                    f'<div class="col-{side}"></div>\n' \
                    f'<div class="col-{middle}">\n'
            self.write(content)
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
            else:
                _log.error(f"Unknown text mark type '{t}'!")
            return text

        def write(self, content):
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
