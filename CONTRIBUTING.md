<!-- TODO Add full contribution guide -->

# Contributing Translations

We welcome translations for `django-unfold`! To add a new language:

1. Ensure you have Django and `gettext` installed.
2. Change current directory to `src/unfold`.
3. Generate message files for new language:

```bash
django-admin makemessages -l <language_code>
```

4. Edit the generated `.po` file in `locale/<language_code>/LC_MESSAGES/django.po` and provide translations.
5. Compile messages:

```bash
django-admin compilemessages
```
