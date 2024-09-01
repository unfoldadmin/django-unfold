[![screenshot-light](https://github.com/unfoldadmin/django-unfold/assets/10785882/291e69c9-abdd-4f7e-a0d6-2af210a9013a#gh-light-mode-only)](https://github.com/unfoldadmin/django-unfold/assets/10785882/291e69c9-abdd-4f7e-a0d6-2af210a9013a#gh-light-mode-only)

[![screenshot-dark](https://github.com/unfoldadmin/django-unfold/assets/10785882/94a2e90f-924a-4aaf-b6d9-cb1592000c55#gh-dark-mode-only)](https://github.com/unfoldadmin/django-unfold/assets/10785882/94a2e90f-924a-4aaf-b6d9-cb1592000c55#gh-dark-mode-only)

## Unfold Django Admin Theme

[![Build](https://img.shields.io/github/actions/workflow/status/unfoldadmin/django-unfold/release.yml?style=for-the-badge)](https://github.com/unfoldadmin/django-unfold/actions?query=workflow%3Arelease)
[![PyPI - Version](https://img.shields.io/pypi/v/django-unfold.svg?style=for-the-badge)](https://pypi.org/project/django-unfold/)
![Code Style - Ruff](https://img.shields.io/badge/code%20style-ruff-30173D.svg?style=for-the-badge)
![Pre Commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=for-the-badge)

Unfold is a theme for Django admin incorporating most common practices for building full-fledged admin areas. It is designed to work on top of default administration provided by Django.

- **Documentation:** full docs are available at [unfoldadmin.com/docs](https://unfoldadmin.com/docs?utm_medium=github&utm_source=unfold)
- **Unfold:** demo site is available at [unfoldadmin.com](https://unfoldadmin.com?utm_medium=github&utm_source=unfold)
- **Formula:** repository with demo implementation at [github.com/unfoldadmin/formula](https://github.com/unfoldadmin/formula)
- **Turbo:** Django & Next.js boilerplate implementing Unfold at [github.com/unfoldadmin/turbo](https://github.com/unfoldadmin/turbo)

## Are you using Unfold and need a help?

Did you decide to start using Unfold but you don't have time to make the switch from native Django admin? [Get in touch with us](https://unfoldadmin.com/?utm_medium=github&utm_source=unfold) and let's supercharge development by using our know-how.

## Features

- **Visual**: provides a new user interface based on Tailwind CSS framework
- **Sidebar:** simplifies definition of custom sidebar navigation with icons
- **Dark mode:** supports both light and dark mode versions
- **Configuration:** most of the basic options can be changed in settings.py
- **Dependencies:** completely based only on `django.contrib.admin`
- **Actions:** multiple ways how to define actions within different parts of admin
- **WYSIWYG:** built-in support for WYSIWYG (Trix)
- **Array widget:** built-in widget for `django.contrib.postgres.fields.ArrayField`
- **Filters:** custom dropdown, numeric, datetime, and text fields
- **Dashboard:** custom components for rapid dashboard development
- **Inline tabs:** group inlines into tab navigation in the change form
- **Model tabs:** define custom tab navigations for models
- **Fieldset tabs:** merge several fieldsets into tabs in the change form
- **Colors:** possibility to override the default color scheme
- **Changeform modes:** display fields in the change form in compressed mode
- **Third party packages:** default support for multiple popular applications
- **Environment label**: distinguish between environments by displaying a label
- **Nonrelated inlines**: displays nonrelated model as inline in changeform
- **Parallel admin**: support for default admin in parallel with Unfold. [Admin migration guide](https://unfoldadmin.com/blog/migrating-django-admin-unfold/?utm_medium=github&utm_source=unfold)
- **Favicons**: built-in support for configuring various site favicons
- **VS Code**: project configuration and development container is included
