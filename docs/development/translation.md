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
3. Edit translations:
    * Open `locale/<language_code>/LC_MESSAGES/django.po`
    * Add or update translations
4. Compile messages:

    ```bash
    django-admin compilemessages
    ```
