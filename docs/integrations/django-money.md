---
title: django-money
order: 0
description: Integration with django-money, a comprehensive Django application that provides support for storing, retrieving and working with monetary values in your Django projects, seamlessly integrated with Unfold's admin interface for an enhanced user experience.
---

# django-money

Django-money is fully supported in Unfold out of the box, providing seamless integration for handling monetary values in your Django applications. There's no need to add any additional applications to your `INSTALLED_APPS` configuration to enable this functionality. Unfold automatically detects the specialized form widgets provided by django-money and applies appropriate styling to ensure they blend perfectly with the rest of your admin interface.

When Unfold identifies a MoneyField in your models, it automatically applies the custom `UnfoldAdminMoneyWidget` which enhances the presentation of currency inputs. This integration maintains all the powerful features of django-money while ensuring the visual consistency of your admin dashboard. The widget properly handles both the amount input and currency selection dropdown, making monetary value management intuitive for administrators.

Unfold provides a custom widget specifically designed for django-money fields called `UnfoldAdminMoneyWidget`, which can be found in the `unfold.widgets` module. This widget enhances the default django-money input by applying Unfold's design system, ensuring a consistent look and feel throughout your admin interface. The widget automatically handles both the amount and currency selection components, presenting them in a visually appealing and user-friendly format.

For detailed instructions on how to install and configure django-money in your Django project, please refer to the [official django-money documentation](https://django-money.readthedocs.io/en/latest/). The documentation covers all aspects of installation, configuration, and usage, including how to define MoneyField fields in your models and how to work with currency conversions.

[![Django Guardian](/static/docs/integrations/django-money.webp)](/static/docs/integrations/django-money.webp)

You can explore a live demonstration of the django-money integration with Unfold by visiting our [demo site](https://demo.unfoldadmin.com/en/admin/formula/driver/56/change/). This demo showcases how monetary values are displayed and edited within the Unfold admin interface, highlighting the seamless integration between django-money and Unfold's design system.
