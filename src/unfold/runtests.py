import os
import sys

import django
from django.test.runner import DiscoverRunner


def print_versions():
    version_info = f"""
    ** Running tests...
    ** Using Python=={sys.version}
         from {sys.executable}
    ** Using Django=={django.get_version()}
    """
    print(version_info)


def setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unfold.settings_development")
    django.setup()


def run_tests():
    test_runner = DiscoverRunner(
        verbosity=2, interactive=False, shuffle=os.getenv("RANDOM_SEED")
    )
    failures = test_runner.run_tests(["unfold.tests"])
    if failures:
        sys.exit(failures)


if __name__ == "__main__":
    print_versions()
    setup_django()
    run_tests()
