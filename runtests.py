import logging
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

log = logging.getLogger(__name__)


def _run_tests(settings_name: str) -> bool:
    print(f"Using settings: '{settings_name}'")
    os.environ["DJANGO_SETTINGS_MODULE"] = settings_name
    from django.core.management import execute_from_command_line

    execute_from_command_line(
        [
            "manage.py",
            "makemigrations",
            f"--settings={settings_name}",
            "mentions",
        ]
    )

    django.setup()

    # Update value of constants.webmention_api_absolute_url after django
    # setup is complete so we can build strings with resolved reverse_lazy.
    import mentions.tests.util.constants as constants

    constants.webmention_api_absolute_url = (
        f"https://{constants.domain}{constants.webmention_api_relative_url}"
    )

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["mentions.tests"])

    return not bool(failures)


def run_tests_without_celery() -> bool:
    return _run_tests("mentions.tests.config.test_settings_without_celery")


def run_tests_with_celery() -> bool:
    return _run_tests("mentions.tests.config.test_settings_with_celery")


if __name__ == "__main__":
    sys.exit(run_tests_without_celery() and run_tests_with_celery())
