---
title: django-location-field
order: 0
description: Integrate django-location-field with Django Unfold to display beautiful map widgets in your admin interface
---

# django-location-field

[django-location-field](https://github.com/caioariede/django-location-field) is a location field and widget for Django that makes it easy to store and display geographic points on a map.

To integrate it with Django Unfold, first install django-location-field according to its documentation, then add `unfold.contrib.location_field` to your `INSTALLED_APPS` setting **before** `location_field`.
