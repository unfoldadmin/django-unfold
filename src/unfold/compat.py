import django
from django.contrib.admin.views.main import ERROR_FLAG, PAGE_VAR
from django.contrib.admin.views.main import ChangeList as DjangoChangeList

if django.VERSION < (5, 0):

    class ChangeList(DjangoChangeList):
        def __init__(self, request, *args, **kwargs):
            super().__init__(request, *args, **kwargs)
            self.filter_params = dict(request.GET.lists())
            self.filter_params.pop(PAGE_VAR, None)
            self.filter_params.pop(ERROR_FLAG, None)

else:
    ChangeList = DjangoChangeList
