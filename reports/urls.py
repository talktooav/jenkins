from django.conf.urls import url
from .views import *

app_name = "reports"
urlpatterns = [
    url(r'^listing/$', PostLinkTrackAjaxView.as_view(), name='report-ajax-listing'),
    url(r'^reports/$', PostLinkTrackView.as_view(), name='reports'),
    url(r'^reports/download-csv/', DownloadPostLinkTrackView.as_view(), name='post-link-track-download-csv'),
    
    url(r'^reports/(?P<token>.+)/getuserlist/$', PostLinkUserList.as_view(), name="get-postuserlist"),
    url(r'^reports/(?P<token>.+)/getuserlist/listing/', PostLinkUserListAjaxView.as_view(), name="get-postuserlist-ajax-listing"),
    
    url(r'^inactiveusers/$', InactiveUsersView.as_view(), name='inactive-users-listing'),
    url(r'^report/inactiveusers/download-csv/', DownloadInactiveUsersView.as_view(), name='inactive-user-download-csv'),
    url(r'^inactiveusers/listing/$', InactiveUsersAjaxView.as_view(), name='inactive-users-ajax-listing'),
    
    url(r'^inactiveemployees/$', InactiveEmployeesView.as_view(), name='inactive-employees-listing'),
    url(r'^report/inactiveemployees/download-csv/', DownloadInactiveEmployeesView.as_view(), name='inactive-employees-download-csv'),
    url(r'^inactiveemployees/listing/$', InactiveEmployeesAjaxView.as_view(), name='inactive-employees-ajax-listing'),
]
