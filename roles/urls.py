from django.conf.urls import url
from .views import *

app_name    = "roles"
urlpatterns = [
    # url(r'^$', UsersHomeView.as_view(), name='home'),
    url(r'^role/add/$', RoleCreateView.as_view(), name='add-role'),
    url(r'^role/$', RoleListView.as_view(), name='roles'),
    url(r'^listing/$', RoleAjaxView.as_view(), name='ajax-roles-list'),
    url(r'^role/(?P<token>.+)/change/$', RoleUpdateView.as_view(), name="edit-role"),
    url(r'^role/(?P<pk>\d+)/changes_status/$', RoleChangeStatus.as_view(), name='change-status'),
    # ~ url(r'^role/(?P<pk>\d+)/delete/$', RoleDeleteView.as_view(), name='role-delete')
    url(r'role/delete/$', RoleDeleteView.as_view(), name='role-delete')
]

