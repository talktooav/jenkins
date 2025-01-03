from django.conf.urls import url
from .views import *

app_name = "userentity"
urlpatterns = [
    url(
        r'^userentity/add/$', UserEntityCreateView.as_view(),
        name='add-userentity'),
    url(
        r'^userentity/$', UserEntityListView.as_view(), name='userentity'),
    url(
        r'^listing/$', UserEntityAjaxView.as_view(),
        name='userentity-ajax-listing'),
    url(
        r'^userentity/(?P<token>.+)/change/$', UserEntityUpdateView.as_view(),
        name="edit-userentity"),
    # ~ url(
    # r'^delete/(?P<pk>\d+)/delete/$', DeleteProfileUpdateView.as_view(),
    # name="delete"),
    url(
        r'^userentity/delete/$', UserEntityDeleteView.as_view(),
        name='delete-userentity'),
]
