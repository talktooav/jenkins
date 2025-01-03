from django.db import models
from americana.utils import cust_timezone
from django.contrib.postgres.fields import ArrayField
from jobusers.models import JobUsers
from postcategory.models import PostCategory
from americana.constants import POST__TYPE_CHOICES, FILE__TYPE_CHOICES, APPROVE_STATUS_CHOICES,POST_LANGUAGE

class Posts(models.Model):
    
    post_type = models.CharField(max_length=30, choices=POST__TYPE_CHOICES)
    user = models.ForeignKey(JobUsers, on_delete = models.PROTECT, null= True)
    post_category = models.ForeignKey(PostCategory, on_delete = models.PROTECT, null= True)
    title = models.JSONField(default=dict)
    description = models.JSONField(default=dict)
    post_image = models.JSONField(default=list)
    post_file = models.JSONField(default=list)
    file_type = models.CharField(max_length=30, choices=FILE__TYPE_CHOICES, blank = True, null= True)
    is_entity = models.IntegerField(default=0) 
    approve_status = models.IntegerField(choices=APPROVE_STATUS_CHOICES, default=0 )
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    verified_at = models.DateTimeField(auto_now_add=False, blank = True, null=True)
    reactions = models.JSONField(default=list)
    createdAt = models.DateTimeField(default=cust_timezone())
    updatedAt = models.DateTimeField(auto_now_add=True, null=True)
    brand_id = models.IntegerField(default=0)
    post_language = models.IntegerField(choices=POST_LANGUAGE, null=True, default=0)
    like_count = models.IntegerField(default=0)
    total_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    heart_count = models.IntegerField(default=0,null=True)
    shock_count = models.IntegerField(default=0,null=True)
    smile_count = models.IntegerField(default=0,null=True)
    created_by = models.IntegerField(default=0)
    updated_by = models.IntegerField(default=0)
    post_author = models.CharField(max_length=6, default='') # if one it means author is admin
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        db_table = 'amrc_posts'
        
    def __str__(self):
        return str(self.title)


class PostActivities(models.Model):
    user        =   models.ForeignKey(JobUsers, on_delete = models.PROTECT, null=True)
    post        =   models.ForeignKey(Posts, on_delete = models.PROTECT, null=True)
    option_name =   models.CharField(max_length=255, blank=True, null=True)
    option_val  =   models.TextField(blank=True)
    extra       =   models.CharField(max_length=255, blank=True, null=True)
    createdAt  =   models.DateTimeField(default=cust_timezone())
    updatedAt  =   models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        db_table = 'amrc_post_activities'
        
    def __str__(self):
        return str(self.option_name)


class PostsReaction(models.Model):

    post               =   models.ForeignKey(Posts, on_delete=models.PROTECT, null=True)
    user               =   models.ForeignKey(JobUsers, on_delete = models.PROTECT, null=True)
    reaction           =   models.IntegerField(default=0)
    createdAt          =   models.DateTimeField(default=cust_timezone())
    updatedAt          =   models.DateTimeField(auto_now_add=True, null=True)
    post_track_status  =   models.BooleanField(default = False)
    
    class Meta:
        db_table = 'amrc_post_reactions'
    
    def __str__(self):
        return str(self.post_id__title)


class PostComments(models.Model):
    user       =   models.ForeignKey(JobUsers, on_delete = models.PROTECT, null=True)
    post       =   models.ForeignKey(Posts, on_delete = models.PROTECT, null=True)
    comment    =   models.TextField(blank=True)
    createdAt  =   models.DateTimeField(default=cust_timezone())
    updatedAt  =   models.DateTimeField(auto_now_add=True, null=True)

    created_by     =   models.IntegerField(default=0)
    updated_by     =   models.IntegerField(default=0)
    ip_address     = models.GenericIPAddressField(blank=True, null=True)
    is_deleted     =   models.BooleanField(default = False)
    
    class Meta:
        db_table = 'amrc_post_comments'
        
    def __str__(self):
        return str(self.post_id__title)
        
class File(models.Model):
    existingPath = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=50)
    eof = models.BooleanField()
    
    class Meta():
        db_table = 'amrc_file'
        default_permissions = ()

