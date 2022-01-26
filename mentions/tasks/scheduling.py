import logging

from django.conf import settings
from django.http import QueryDict

from .incoming_webmentions import process_incoming_webmention
from .outgoing_webmentions import process_outgoing_webmentions
from ..models import PendingIncomingWebmention, PendingOutgoingContent

log = logging.getLogger(__name__)


def _use_celery():
    return getattr(settings, "WEBMENTIONS_USE_CELERY", True)


def handle_incoming_webmention(http_post: QueryDict, client_ip: str) -> None:
    source = http_post["source"]
    target = http_post["target"]

    use_celery = _use_celery()

    if use_celery:
        process_incoming_webmention.delay(
            source=source,
            target=target,
            client_ip=client_ip,
        )

    else:
        # Needs to be handled in manage.py task later
        PendingIncomingWebmention.objects.create(
            source=source,
            target=target,
            sent_by=client_ip,
        )


def handle_outgoing_webmention(absolute_url: str, text: str) -> None:
    use_celery = _use_celery()

    if use_celery:
        process_outgoing_webmentions.delay(absolute_url, text)

    else:
        # Needs to be handled in manage.py task later
        PendingOutgoingContent.objects.create(
            absolute_url=absolute_url,
            text=text,
        )


def handle_pending_webmentions(incoming: bool = False, outgoing: bool = False):
    """Process any pending webmentions as a batch.

    This may take a while as it may involve a lot of network requests, depending on the pending content.
    Only required when Celery is not used.
    """

    if incoming:
        for wm in PendingIncomingWebmention.objects.all():
            log.info(f"Processing webmention from {wm.source_url}...")
            process_incoming_webmention(wm.source_url, wm.target_url, wm.sent_by)
            wm.delete()

    if outgoing:
        for wm in PendingOutgoingContent.objects.all():
            log.info(f"Processing outgoing webmentions for content {wm.absolute_url}")
            process_outgoing_webmentions(wm.absolute_url, wm.text)
            wm.delete()
