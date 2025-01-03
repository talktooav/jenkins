from django.conf.urls import url
from .views import *

app_name = "rewards"
urlpatterns = [
    
    url(r'^stores/add/$', StoresCreateView.as_view(), name='add-stores'),
    url(r'^stores/$', StoresListView.as_view(), name='stores'),
    url(r'^stores/listing/$', StoresAjaxView.as_view(), name='stores-ajax-listing'),
    url(r'^stores/(?P<token>.+)/change/$', StoresUpdateView.as_view(), name="edit-stores"),
    url(r'^stores/delete/$', StoresDeleteView.as_view(), name='delete-stores'),
    
    url(r'^rewards/add/$', RewardsCreateView.as_view(), name='add-rewards'),
    url(r'^rewards/$', RewardsListView.as_view(), name='rewards'),
    url(r'^listing/$', RewardsAjaxView.as_view(), name='rewards-ajax-listing'),
    url(r'^rewards/(?P<token>.+)/change/$', RewardsUpdateView.as_view(), name="edit-rewards"),
    url(r'^rewards/delete/$', RewardsDeleteView.as_view(), name='delete-rewards'),

    url(r'^points/add/$', PointsCreateView.as_view(), name='add-points'),
    url(r'^points/$', PointsListView.as_view(), name='points'),
    url(r'^points/listing/$', PointsAjaxView.as_view(), name='points-ajax-listing'),
    url(r'^points/(?P<token>.+)/change/$', PointsUpdateView.as_view(), name="edit-points"),
    url(r'^points/delete/$', PointsDeleteView.as_view(), name='delete-points'),
]
