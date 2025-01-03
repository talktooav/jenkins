from django.conf.urls import url
from .views import *

app_name = "pushNotification"
urlpatterns = [
    url(r'^pushnotification/add/$', PushCreateView.as_view(), name='add-pushnotification'),
    url(r'^listing/$', PushAjaxView.as_view(), name='pushnotification-ajax-listing'),
    url(r'^pushnotification/$', PushListView.as_view(), name='pushnotification'),
    url(r'^pushnotification/(?P<token>.+)/change/$', PushUpdateView.as_view(), name="edit-pushnotification"),
    # ~ url(r'^delete/(?P<pk>\d+)/delete/$', DeleteProfileUpdateView.as_view(), name="delete"),
    url(r'^pushnotification/delete/$', PushDeleteView.as_view(), name='delete-pushnotification'),
]

