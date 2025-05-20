from django.core.paginator import Page, Paginator
from django.utils.functional import cached_property


class InfinitePage(Page):
    def has_next(self):
        if len(self.object_list) == 0:
            return False

        return self.number < self.paginator.num_pages


class InfinitePaginator(Paginator):
    template_name = "unfold/helpers/pagination_infinite.html"

    @cached_property
    def count(self):
        return 9_999_999_999

    def _get_page(self, *args, **kwargs):
        return InfinitePage(*args, **kwargs)
