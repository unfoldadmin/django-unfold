#!/usr/bin/env python3

# This file includes code adapted from django-jazzmin (https://github.com/farridav/django-jazzmin)
# Copyright (c) David Farrington
# Licensed under the MIT License

import pathlib
from itertools import chain

import click
import django
import polib

THIS_DIR = pathlib.Path(__file__)
LOCALE_DIR = THIS_DIR.parent.parent / "src" / "unfold" / "locale"
LOCALES = [p.name for p in LOCALE_DIR.iterdir()]
DJANGO_PATH = pathlib.Path(django.__path__[0])


@click.command()
@click.argument("prune", type=click.Choice(LOCALES))
def main(prune: str):
    """
    Remove the django provided strings

    e.g - ./prune_locale.py de
    """
    our_po = polib.pofile(LOCALE_DIR / prune / "LC_MESSAGES" / "django.po")
    admin_po = polib.pofile(
        DJANGO_PATH
        / "contrib"
        / "admin"
        / "locale"
        / "en"
        / "LC_MESSAGES"
        / "django.po"
    )
    admindocs_po = polib.pofile(
        DJANGO_PATH
        / "contrib"
        / "admindocs"
        / "locale"
        / "en"
        / "LC_MESSAGES"
        / "django.po"
    )

    existing_strings = {x.msgid for x in chain(admin_po, admindocs_po)}
    new_po = polib.POFile()
    new_po.metadata = our_po.metadata
    for po in our_po:
        if po.msgid not in existing_strings:
            new_po.append(po)

    new_po.save(LOCALE_DIR / prune / "LC_MESSAGES" / "django.po")


if __name__ == "__main__":
    main()
