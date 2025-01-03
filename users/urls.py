from django.conf.urls import url
from .views import *
from account.views import user_upload
app_name = "users"
urlpatterns = [
        url(r'^listing', UserAjaxView.as_view(), name='user-ajax-view'),
        url(r'^upload-user', user_upload.as_view(), name='user-upload'),
        url(r'^selectenterprise',
            ChangeEnterprise.as_view(), name='select-enterprise'),
        url(r'^password_change/$',
            ChangePasswordView.as_view(), name='change-password'),
        url(r'^user/$', UserListView.as_view(), name='users'),
        url(r'^user/add/$', RegisterView.as_view(), name='add-user'),
        url(r'^user/(?P<token>.+)/change/$',
            UserProfileUpdateView.as_view(),
            name="edit-user-profile"),
        url(r'^user/delete/$', UserDelView.as_view(), name='user-delete')
]
