from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Q

from jobusers.models import JobUsers
from post.models import Posts


class DashboardList(ListView):

    @method_decorator(login_required)
    def get(self, request):
        context = {
            "title": "Hello World!",
            "content": " Welcome to the homepage.",

        }
        # total number of users
        user_obj = JobUsers.objects.filter(

            Q(is_active=True)
        ).order_by('-id').values('id')

        total_user_count = user_obj.count()
        if total_user_count == 0:
            total_user_count = 'No'

        # get top 5 users
        user_obj = JobUsers.objects.filter(
                        Q(is_active=True)).order_by('-id')[:5].values(
                        'id', 'employee_name', 'employee_code', 'cost_name',
                        'createdAt', 'job_role__name')

        # total number of posts
        posts_obj = Posts.objects.filter(

            Q(is_deleted=False)
        ).order_by('-id').values('id')

        total_post_count = posts_obj.count()
        if total_post_count == 0:
            total_post_count = 'No'

        # total number of Survey
        poll_obj = Posts.objects.filter(
            Q(is_deleted=False, post_type='poll')
        ).order_by('-id').values('id')

        total_survey_count = poll_obj.count()
        if total_survey_count == 0:
            total_survey_count = 'No'

        # get top 5 posts
        posts_obj = Posts.objects.filter(
            Q(is_deleted__icontains=False)).values(
                'id', 'title', 'description', 'post_type', 'user_id__employee_code',
                'post_category__name', 'post_image', 'post_file',
                'file_type', 'like_count',
                'comment_count', 'approve_status',
                'status').order_by('-id')[:5]

        context["user_data"] = user_obj
        context["posts_obj"] = posts_obj
        context["total_user_count"] = total_user_count
        context["total_post_count"] = total_post_count
        context["total_survey_count"] = total_survey_count
        # ~ print('user_dashboard data=>',user_obj)
        # ~ if request.user.is_authenticated:

        return render(request, "dashboard.html", context)
