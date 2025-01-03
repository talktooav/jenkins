from django.conf.urls import url
from .views import *

app_name = "polls"
urlpatterns = [
    url(r'^poll/add/$', PollCreateView.as_view(), name='add-poll'),
    url(r'^listing/$', PollAjaxView.as_view(), name='poll-ajax-listing'),
    url(r'^poll/$', PollListView.as_view(), name='poll'),
    url(r'^poll/(?P<token>.+)/change/$', PollUpdateView.as_view(), name="edit-poll"),
    url(r'^poll/delete/$', PollDeleteView.as_view(), name='delete-poll'),
]
