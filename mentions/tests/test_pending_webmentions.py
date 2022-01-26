from unittest import TestCase

from mentions.models import PendingIncomingWebmention
from mentions.tasks.scheduling import handle_pending_webmentions


class PendingTests(TestCase):
    def setUp(self) -> None:
        raise NotImplemented()

    def test_pending_incoming(self):
        handle_pending_webmentions(incoming=True)

        raise NotImplemented()

    def test_pending_outgoing(self):

        handle_pending_webmentions(outgoing=True)

        raise NotImplemented()
