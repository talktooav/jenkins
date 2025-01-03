from django.db import models
from americana.utils import cust_timezone
from jobusers.models import JobUsers


class Products(models.Model):
    
    name 			= models.CharField(max_length=30, null=True)
    description 	= models.TextField(blank=True, null=True)
    product_image 	= models.JSONField(default=dict)
    price 			= models.BigIntegerField(default=0,null=True)
    createdAt 		= models.DateTimeField(default=cust_timezone())
    updatedAt 		= models.DateTimeField(auto_now_add=True, null=True)
    is_deleted 		= models.BooleanField(default = False)
    created_by 		= models.IntegerField(default=0)
    updated_by 		= models.IntegerField(default=0)
    brand_id 		= models.IntegerField(default=0)
    ip_address 		= models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        db_table = 'amrc_products'
        
    def __str__(self):
        return str(self.title)


class JobUserStore(models.Model):
    
    user            = models.ForeignKey(JobUsers, on_delete = models.PROTECT, null= True)
    product         = models.ForeignKey(Products, on_delete = models.PROTECT, null=True)
    boughtAt        = models.DateTimeField(default=cust_timezone())
    is_deleted      = models.BooleanField(default = False)
    brand_id        = models.IntegerField(default=0)
    ip_address      = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        db_table = 'amrc_job_user_store'
        
    def __str__(self):
        return str(self.product_id__name)