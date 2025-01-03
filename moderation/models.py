from django.db import models
from americana.utils import cust_timezone

class Moderation(models.Model):
    word        = models.CharField(max_length=255)
    description = models.TextField(blank=False, verbose_name='Description')
    status      = models.BooleanField(default=True)
    is_deleted  = models.BooleanField(default=False)
    ip_address  = models.GenericIPAddressField(blank=True, null=True)
    created_by  = models.IntegerField(default=0)
    updated_by  = models.IntegerField(default=0)
    createdAt   = models.DateTimeField(default=cust_timezone())
    updatedAt   = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        db_table = 'amrc_moderation'
    def __str__(self):
        return str(self.word)
