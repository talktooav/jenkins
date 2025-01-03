from django.db import models
from americana.utils import cust_timezone

class UserEntity(models.Model):
    name        = models.CharField(max_length = 100)
    description = models.TextField(blank=False, verbose_name='Description')
    status      = models.BooleanField(default=True)
    is_deleted  = models.BooleanField(default=False)
    createdAt   = models.DateTimeField(default=cust_timezone())
    updatedAt   = models.DateTimeField(auto_now_add=True, null=True)

    ip_address  = models.GenericIPAddressField(blank=True, null=True)
    created_by  = models.IntegerField(default=0)
    updated_by  = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'amrc_user_entity'
        
    def __str__(self):
        return str(self.name)


