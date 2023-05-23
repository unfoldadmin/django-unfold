import os
import sys

import django

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    django.setup()
    from django.test.runner import DiscoverRunner

    test_runner = DiscoverRunner(
        verbosity=2, interactive=False, shuffle=os.getenv("RANDOM_SEED")
    )
    print(f"Testing against Django=={django.get_version()}, Python=={sys.version}")
    failures = test_runner.run_tests(["unfold.tests"])
    if failures:
        sys.exit(failures)
