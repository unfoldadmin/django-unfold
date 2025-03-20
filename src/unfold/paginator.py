from django.core.paginator import Paginator
from django.utils.functional import cached_property


class DumbPaginator(Paginator):
    template_name = "unfold/helpers/pagination_dumb.html"

    @cached_property
    def count(self):
        return 9_999_999_999
