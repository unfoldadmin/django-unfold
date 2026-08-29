---
title: Avatar
order: 3
description:
---

# Avatar

The avatar can be customized by overriding the `avatar_url`, `avatar_badge_variant`, `avatar_badge_count` and `avatar_badge_url` properties on the user model.

```python
from django.db import models
from django.templatetags.static import static


class User(AbstractUser):
    @property
    def avatar_url(self) -> str:
        return static("demo/images/avatar.webp")

    @property
    def avatar_badge_variant(self) -> str | None:
        # Options: danger, warning, success, info, primary, default
        return "primary"

    @property
    def avatar_badge_count(self) -> str | int | None:
        return Ticket.objects.filter(assigned_to=self, status=TicketStatus.OPEN).count()

    @property
    def avatar_badge_url(self) -> str | None:
        return "https://example.com"
```
