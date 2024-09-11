import logging
import re

from urllib.parse import urlparse, parse_qs

_log = logging.getLogger(__name__)


class Attachment(object):

    UUID_REGEX = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

    def __init__(self, id):
        self.id = id
        self.media_id = None
        self.name = None
        self.content_type = None
        self.data = None

    def populate(self, http_response):
        # Get additional info of the attachment (e.g. UUID, content type, ...)
        url = urlparse(http_response.url)
        uuid_match = re.search(self.UUID_REGEX, url.path)
        if uuid_match is not None:
            self.media_id = uuid_match[0]
        else:
            _log.warn(f'No media ID found for attachment #{self.id}')
        # Get attachment name
        names = parse_qs(url.query).get('name')
        if names is not None:
            self.name = names[0]
        # Get content type
        self.content_type = http_response.headers.get('Content-Type')
        # Get content
        self.data = http_response.content

    def __str__(self):
        return f'{self.id}: {self.name} ({self.media_id})'
