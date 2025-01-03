from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.conf.urls import url
from users.views import LoginView
from django.contrib.auth.views import LogoutView
from .views import DashboardList

urlpatterns = [
    re_path(r'^api/', include('account.urls')),
    # ~ path('admin/', admin.site.urls),
    url(
        r'^$', LoginView.as_view(template_name='login.html'),
        name='login'),
    url(
        r'^login/$', LoginView.as_view(template_name='login.html'),
        name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardList.as_view(), name='dashboard'),
    path('<slug:slug>/users/', include("users.urls", namespace='users'), name='users'),
    path('roles/', include("roles.urls", namespace='roles'), name='roles'),
    path(
        'moderation/', include("moderation.urls", namespace='moderation'),
        name='moderation'),
    path(
        'userentity/', include("userentity.urls", namespace='userentity'),
        name='userentity'),
    path(
        'jobrole/', include("jobrole.urls", namespace='jobrole'),
        name='jobrole'),
    path(
        'jobusers/', include("jobusers.urls", namespace='jobusers'),
        name='jobusers'),
    path(
        'americanaStore/', include("americanaStore.urls", namespace='americanaStore'),
        name='americanaStore'),
    path(
        'postcategory/',
        include("postcategory.urls", namespace='postcategory'),
        name='postcategory'),
    path('post/', include("post.urls", namespace='post'), name='post'),
    path(
        'reports/', include("reports.urls", namespace='reports'),
        name='reports'),
    path(
        'quiz/', include("quiz.urls", namespace='quiz'),
        name='quiz'),
    path(
        'rewards/', include("rewards.urls", namespace='rewards'),
        name='rewards'),
    path(
     'pushnotification/', include("pushNotification.urls",
     namespace='pushnotification'), name='pushnotification'),
    path('polls/', include("polls.urls", namespace='polls'), name='polls'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
