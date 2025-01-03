from django.conf.urls import url
from .views import *

app_name = "moderation"
urlpatterns = [
    url(r'^moderation/add/$', ModerationCreateView.as_view(), name='add-moderation'),
    url(r'^moderation/$', ModerationListView.as_view(), name='moderation'),
    url(r'^listing/$', ModerationAjaxView.as_view(), name='moderation-ajax-listing'),
    url(r'^moderation/(?P<token>.+)/change/$', ModerationUpdateView.as_view(), name="edit-moderation"),
    # ~ url(r'^delete/(?P<pk>\d+)/delete/$', DeleteProfileUpdateView.as_view(), name="delete"),
    url(r'^moderation/delete/$', ModerationDeleteView.as_view(), name='delete-moderation'),
]
