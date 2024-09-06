import logging
import json

from datetime import date

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

        def __init__(self, header_offset=0):
            self.html = ''
            self.header_offset = header_offset

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

        def write_element(self, t, attrs, content):
            if t == 'paragraph':
                self.write_paragraph(attrs, content)
            elif t == 'date':
                self.write_date(attrs, content)
            elif t == 'heading':
                self.write_heading(attrs, content)
            else:
                _log.error(f"Unknown element type '{t}'!")

        def write(self, content):
            for el in content:
                if 'type' not in el:
                    _log.error('No type defined for document element!')
                    continue
                # Handle simple text elements here
                t = el['type']
                if t == 'text':
                    self.html += el.get('text')
                    continue
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
