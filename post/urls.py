from django.conf.urls import url
from .views import *

app_name = "post"
urlpatterns = [
    url(r'^post/add/$', PostCreateView.as_view(), name='add-post'),
    url(r'^post/add-file/$', PostFileView.as_view(), name='add-post-image'),
    url(r'^listing/$', PostAjaxView.as_view(), name='post-ajax-listing'),
    url(r'^post/$', PostListView.as_view(), name='post'),
    url(r'^post/(?P<token>.+)/change/$', PostUpdateView.as_view(), name="edit-post"),
    # ~ url(r'^delete/(?P<pk>\d+)/delete/$', DeleteProfileUpdateView.as_view(), name="delete"),
    url(r'^post/delete/$', PostDeleteView.as_view(), name='delete-post'),
]
