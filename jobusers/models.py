from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from americana.utils import cust_timezone
from jobrole.models import JobRoles
from userentity.models import UserEntity
from americana.constants import GENDER_CHOICES

class JobUsers(models.Model):
    
    # ~ email       = models.EmailField(_('email address'), unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,10}$', message="Phone number must be entered 10 digits valid phone no.")
    employee_code = models.CharField(max_length=30, unique=True)
    employee_name = models.CharField(max_length=50, blank=True, null=True)
    job_role      = models.ForeignKey(JobRoles, on_delete=models.CASCADE, null= True)
    gender        = models.CharField(max_length=1, choices=GENDER_CHOICES)
    market        = models.CharField(max_length=50,blank=True, null=True)
    city          = models.CharField(max_length=50,blank=True, null=True)
    nationality   = models.CharField(max_length=50,blank=True, null=True)
    date_of_birth = models.DateField(auto_now_add=False, blank=True, null=True)
    hire_date     = models.CharField(max_length=50, blank=True, null=True)
    cc_code       = models.CharField(max_length=30, blank=True, null=True)
    cost_name     = models.CharField(max_length=50, blank=True, null=True)
    # ~ phone     = models.CharField(validators=[phone_regex], max_length=10, unique=True)
    
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    updated_by = models.IntegerField(default=0)
    language = models.IntegerField(blank=True,null=True,default=0)
    brand_id = models.IntegerField(default=0)
    device_id = models.TextField(max_length=255,blank=True, null=True)
    device_token = models.CharField(max_length=255,blank=True, null=True)
    status = models.BooleanField(default=True)
    entity = models.ForeignKey(UserEntity, on_delete=models.PROTECT, null=True)
    is_logged = models.BooleanField(default=False)
    is_active = models.BooleanField(_('active'), default=False)
    logged_in_time = models.DateField(auto_now_add=False, blank=True, null=True)
    # ~ userProfileImage = models.ImageField(upload_to='profile_pic', height_field=None, width_field=None,blank=True, null=True)
    userProfileImage = models.JSONField(blank=True, default=dict)
    user_point = models.BigIntegerField(default=0, help_text='User total point')
    createdAt = models.DateTimeField(default=cust_timezone())
    updatedAt = models.DateTimeField(auto_now_add=True, null=True)
    
    # ~ REQUIRED_FIELDS  = ['email', 'employee_code']

    class Meta:
        db_table = 'amrc_job_users'
        
    def __str__(self):
        return self.employee_code
        

class PhoneOTP(models.Model):
    
    phone_regex = RegexValidator(regex = r'^\+?1?\d{9,10}$', message ="Phone number must be entered in the format: '+999999999'. Up to 14 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=10, unique=True)
    otp = models.CharField(max_length=9, blank=True, null=True)
    count = models.IntegerField(default=0, help_text='Number of otp sent')
    verified = models.BooleanField(default=False, help_text='If otp verification got successful')
    
    class Meta:
        db_table = 'amrc_phone_otp'
        
    def __str__(self):
        return str(self.phone) + ' is sent ' + str(self.otp)


class UserActivity(models.Model):
    by_user = models.ForeignKey(JobUsers, on_delete=models.PROTECT)
    option_name = models.CharField(max_length=255)
    option_val = models.TextField()
    extra = models.CharField(max_length=255, blank=True, null=True)
    createdAt = models.DateTimeField(default=cust_timezone())
    updatedAt = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        db_table = 'amrc_job_user_activity'
        
    def __str__(self):
        return str(self.option_name)


class Job_User_Login_Log(models.Model):
    
    user_id = models.IntegerField(default=0)
    enterprise_id = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    login_time = models.DateTimeField(default=cust_timezone())
    createdAt = models.DateTimeField(default=cust_timezone())
    
    class Meta:
        db_table = 'amrc_job_user_login_logs'


class Job_User_Points_Log(models.Model):
    
    user = models.ForeignKey(JobUsers, on_delete=models.PROTECT)
    point_id = models.IntegerField(default=0)
    point_action = models.CharField(max_length=30, blank=True, null=True)
    action_type = models.CharField(max_length=4, blank=True, null=True)
    point = models.IntegerField(default=0)
    point_desc = models.TextField(default=0)
    createdAt = models.DateTimeField(default=cust_timezone())
    
    class Meta:
        db_table = 'amrc_job_user_points_log'




