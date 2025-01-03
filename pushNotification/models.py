from django.db import models
from americana.utils import cust_timezone
from jobusers.models import JobUsers
from jobrole.models import JobRoles


class Notification(models.Model):

    TYPE_CHOICES = (('normal', 'Normal Notification'), ('update', 'Update Notification'))

    p_id            =   models.IntegerField(default=0)
    n_type          =   models.CharField(max_length=30, choices=TYPE_CHOICES, default='normal')
    from_user_id    =   models.ForeignKey(JobUsers, on_delete=models.CASCADE)
    from_user_type  =   models.CharField(max_length=150)
    to_user_id      =   models.IntegerField(default=0)
    to_user_type    =   models.CharField(max_length=150, blank=True, null=True)
    noti_type       =   models.CharField(max_length=50)
    title           =   models.CharField(max_length=255)
    sub_title       =   models.CharField(max_length=255, blank=True, null=True)
    data            =   models.TextField(blank=True, null=True)
    detail          =   models.JSONField(blank=True, null=True)
    read_at         =   models.DateField(auto_now_add=False, blank=True, null=True)
    createdAt       =   models.DateTimeField(default=cust_timezone())
    updatedAt       =   models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        db_table = 'amrc_notification'
        
    def __str__(self):
        return str(self.title)


class PushNotification(models.Model):
    
    title              =   models.CharField(max_length = 255,null=True)
    link               =   models.URLField(max_length = 255,null=True)
    user               =   models.ForeignKey(JobUsers, on_delete = models.CASCADE, null=True) #to notification
    description        =   models.TextField(blank = False, verbose_name = 'Description',null=True)
    job_role           =   models.ForeignKey(JobRoles, on_delete = models.CASCADE, null= True)
    sent_status        =   models.IntegerField(default=0)
    schedule_date_time =   models.CharField(max_length = 255,default='')
    is_deleted         =   models.BooleanField(default = False)
    createdAt          =   models.DateTimeField(default=cust_timezone())
    
    class Meta:
        db_table = 'amrc_push_notification'
