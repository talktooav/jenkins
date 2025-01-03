from django.conf.urls import url

#from products.views import UserProductHistoryView
from .views import *

app_name = "jobusers"
urlpatterns = [
        # ~ url(r'^$', UsersHomeView.as_view(), name='home'),
        url(r'^jobuser/$', JobUserListView.as_view(), name='jobusers'),
        url(r'^jobuser/listing', JobUserAjaxView.as_view(), name='jobuser-ajax-view'),
        url(r'^jobuser/upload-users', jobUserUploadView.as_view(), name='jobuser-upload'),
        # ~ url(r'^email/resend-activation/$', UserEmailActivateView.as_view(), name='resend-activation'),
        # ~ url(r'^email/confirm/(?P<key>[0-9A-Za-z]+)/$', UserEmailActivateView.as_view(), name='email-activate'),
        url(r'^jobuser/add/$', JobUserRegisterView.as_view(), name='add-job-user'),
        url(r'^jobuser/(?P<token>.+)/change/$', JobUserProfileUpdateView.as_view(), name="edit-job-user"),
        url(r'^jobuser/delete/$', JobUserDeleteView.as_view(), name='jobuser-delete')
]

