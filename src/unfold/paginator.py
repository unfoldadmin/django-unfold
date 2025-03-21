from django.core.paginator import Paginator
from django.utils.functional import cached_property


class InfinitePaginator(Paginator):
    template_name = "unfold/helpers/pagination_infinite.html"

    @cached_property
    def count(self):
        return 9_999_999_999
