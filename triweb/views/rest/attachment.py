import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound

from triweb.views import View

_log = logging.getLogger(__name__)


class AttachmentView(View):

    @view_config(route_name='rest.attachment')
    def view(self):
        issue_id = self.request.matchdict['issue_id']
        media_id = self.request.matchdict['id']
        # Get max age from the query string (optional)
        max_age = self.request.params.get('max_age')
        if max_age is not None:
            try:
                max_age = int(max_age)
            except:
                _log.warn(f"Expected int for max_age not '{max_age}'!")
                max_age = None
        # First try to get the attachment from the cache
        att = self.request.jira.get_attachment_from_cache(media_id, max_age)
        if att is None:
            # If the attachment is not yet in the cache, it is needed to get
            # all the attachments of the issue, otherwise it is not possible to
            # get the attachments by its media ID.
            self.request.jira.get_attachments(issue_id, max_age)
            # Get attachment
            att = self.request.jira.get_attachment(media_id)
        # Create response
        if att is None:
            raise HTTPNotFound()
        response = self.request.response
        response.content_type = att.content_type
        response.body = att.data
        return response