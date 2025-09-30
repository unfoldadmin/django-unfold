---
title: Translations
order: 3
description: Learn how to contribute translations for django-unfold using Django's built-in internationalization framework.
---

# Translations

Add new language support to `django-unfold` using Django's internationalization framework.

## Prerequisites

- Django installed
- `gettext` available

## Workflow

1. **Navigate to source directory:**

   ```bash
   cd src/unfold
    ```

2. Create message files for your language:

    ```bash
    django-admin makemessages -l <language_code>
    ```

3. Prune Django default translations

   ```bash
   ../../scripts/prune_locale.py <language_code>
   ```

4. Edit translations:
    * Open `locale/<language_code>/LC_MESSAGES/django.po`
    * Add or update translations

5. Compile messages:

    ```bash
    django-admin compilemessages
    ```
