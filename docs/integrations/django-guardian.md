---
title: django-guardian
order: 0
description: Integration with django-guardian, a powerful object-level permissions system for Django that seamlessly integrates with Unfold admin interface for enhanced access control management.
---

# django-guardian

Integrating django-guardian with Unfold is straightforward and requires minimal configuration. Simply add `unfold.contrib.guardian` to your `INSTALLED_APPS` at the beginning of your settings file. This addition will override all templates provided by django-guardian, ensuring a seamless visual integration with the Unfold admin interface. The integration maintains all the functionality of django-guardian while providing an improved user experience consistent with Unfold's design principles.

After installation and configuration, an "Object permissions" button will be displayed on the change form detail page, allowing you to manage object-level permissions directly from the admin interface. This button provides access to a comprehensive permissions management panel where administrators can assign specific permissions to users and groups for individual objects, enabling fine-grained access control throughout your application.

For detailed installation instructions for django-guardian, please refer to the [official documentation](https://django-guardian.readthedocs.io/en/stable/installation/). The documentation provides comprehensive guidance on how to properly set up django-guardian in your Django project, including all necessary configuration steps and requirements.

[![Django Guardian](/static/docs/integrations/django-guardian.webp)](/static/docs/integrations/django-guardian.webp)

A live demo of the [django-guardian integration with Unfold](https://demo.unfoldadmin.com/en/admin/formula/driver/56/permissions/) is available for you to explore. This demo showcases the object permissions interface and how it seamlessly integrates with the Unfold admin design.
