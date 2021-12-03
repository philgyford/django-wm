from django.core.management import BaseCommand

from mentions.tasks.scheduling import handle_pending


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "pending_type",
            choices=["all", "incoming", "outgoing"],
            default="all",
            nargs="?",
            help="Choose to process incoming webmentions or outgoing webmentions. "
            "Default is 'all' which will do both incoming and outgoing.",
        )

    def handle(self, *args, **options):
        pending_type = options["pending_type"]
        incoming = pending_type == "incoming"
        outgoing = pending_type == "outgoing"

        if pending_type == "all":
            incoming = True
            outgoing = True

        handle_pending(incoming=incoming, outgoing=outgoing)
