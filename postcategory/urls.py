from django.conf.urls import url
from .views import *

app_name = "postcategory"
urlpatterns = [
    url(r'^postcategory/add/$', PostCategoryCreateView.as_view(), name='add-postcategory'),
    url(r'^postcategory/$', PostCategoryListView.as_view(), name='postcategory'),
    url(r'^listing/$', PostCategoryAjaxView.as_view(), name='postcategory-ajax-listing'),
    url(r'^postcategory/(?P<token>.+)/change/$', PostCategoryUpdateView.as_view(), name="edit-postcategory"),
    # ~ url(r'^delete/(?P<pk>\d+)/delete/$', DeleteProfileUpdateView.as_view(), name="delete"),
    url(r'^postcategory/delete/$', PostCategoryDeleteView.as_view(), name='delete-postcategory'),
]
