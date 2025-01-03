import os
from django.http.request import QueryDict, MultiValueDict
from django.db.models import Q
from jobusers.models import JobUsers 
from users.models import User
from post.models import Posts, PostActivities
from pushNotification.models import Notification
from americana.utils import timezones
import json

from datetime import datetime, date, timedelta
from .serializers import CustomUserSerializer, PostActivitiesSerializer, PostSerializer, NotificationSerializer
from django_cron import CronJobBase, Schedule

class MyCronJob(CronJobBase):
    # ~ RUN_EVERY_MINS = 1 # every 2 min
    RUN_AT_TIMES = ['00:01']

    # ~ schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'account.my_cron_jobs'
    
    def do(self):
        today_time = date.today()
        brands = User.objects.filter(user_type='brand').values('id')
        print('brands', brands)
        
        if not brands:
            brands = [{'id' : 0}]
            
        for brand in brands:
            brand_id = brand['id']
        
            todayBirthdayPost = Posts.objects.filter(Q(createdAt__startswith=date.today()), Q(post_type='birthday'), Q(brand_id=brand_id))
            # ~ print('todayBirthdayPost', todayBirthdayPost)
            if todayBirthdayPost.exists() != True:
                queryset = JobUsers.objects.filter(Q(date_of_birth__month=today_time.month), Q(date_of_birth__day=today_time.day), Q(brand_id=brand_id))
                if queryset:
                    arr = []
                    for user in queryset:
                        title = "It's @"+user.employee_name
                        
                        data = {"type": "birthday", "sub_title": "birthday today give him good wishes", "link":""}
                        data['date_of_birth'] = str(user.date_of_birth)
                        json_data= json.dumps(data)
                        # add_notification(user['id'],'','','global',title,json_data)
                        data = {"user_id": str(user.id), "employee_name": str(user.employee_name), "userProfileImage": str(user.userProfileImage), "date_of_birth": str(user.date_of_birth), "gender": str(user.gender)}
                        arr.append(data)
                    if arr:
                        jsondata = json.dumps(arr)
                        # ~ params = <QueryDict: {'employee_id': ['1'], 'is_entity': ['0'], 'title': ['Sample'], 'description': ['Test Description'], 'taggedusers': ['1'], 'like_count': ['1'], 'comment_count': ['4'], 'post_category': ['2']}>
                        title = {'english':'Users Birthday', 'arabic':''}
                        desc = {'english':'', 'arabic':''}
                        param_dict = {'title': json.dumps(title), 'description' : json.dumps(desc), 'file_type': 'image', 'post_type': 'birthday', 'approve_status': 1, 'status': True, 'reactions': jsondata, 'createdAt': timezones(), 'brand_id' : user.brand_id}; 
                        query_dict = QueryDict('', mutable=True)
                        query_dict.update(param_dict)
                        post_serialize = PostSerializer(data=query_dict)
                        
                        if post_serialize.is_valid(raise_exception=True):
                            post_serialize.save()
                            
                        # ~ print('post_data', post_serialize.id)
            

        
        

        
