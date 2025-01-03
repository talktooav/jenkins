from django.conf.urls import url
from .views import *

app_name = "americanaStore"
urlpatterns = [
    url(r'^americana-store/add/$', ProductCreateView.as_view(), name='add-product'),
    url(r'^americana-store/listing/$', ProductAjaxView.as_view(), name='product-ajax-listing'),
    url(r'^americana-store/$', ProductListView.as_view(), name='product'),
    url(r'^americana-store/(?P<token>.+)/change/$', ProductUpdateView.as_view(), name="edit-product"),
    # ~ url(r'^delete/(?P<pk>\d+)/delete/$', DeleteProfileUpdateView.as_view(), name="delete"),
    # url(r'^post/delete/$', PostDeleteView.as_view(), name='delete-product'),
    url(r'^userstore/listing/$', UserStoreAjaxView.as_view(), name='userstore-ajax-listing'),
    url(r'^userstore/$', UserStoreListView.as_view(), name='userstore'),
]