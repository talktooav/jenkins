from django.conf.urls import url
from .views import *

app_name = "jobrole"
urlpatterns = [
    url(r'^jobrole/add/$', JobRolesCreateView.as_view(), name='add-jobrole'),
    url(r'^jobrole/$', JobRolesListView.as_view(), name='jobrole'),
    url(r'^listing/$', JobRolesAjaxView.as_view(), name='jobrole-ajax-listing'),
    url(r'^jobrole/(?P<token>.+)/change/$', JobRolesUpdateView.as_view(), name="edit-jobrole"),
    # ~ url(r'^delete/(?P<pk>\d+)/delete/$', DeleteProfileUpdateView.as_view(), name="delete"),
    url(r'^jobrole/delete/$', JobRolesDeleteView.as_view(), name='delete-jobrole'),
]
