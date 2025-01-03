from django.db import models
from americana.utils import cust_timezone
from django.core.exceptions import ValidationError
from jobusers.models import JobUsers
from americana.constants import AWARD_CHOICES
from django.utils import timezone

def validate_date(date):
    if date > timezone.now().date():
        raise ValidationError("Candidate cannot be select in the Future date")

class Store(models.Model):
    store_id=models.CharField(max_length=30)
    name=models.CharField(max_length=255)
    brand_id = models.IntegerField(default=0)
    createdAt = models.DateTimeField(default=cust_timezone())
    updatedAt = models.DateTimeField(auto_now_add=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    updated_by = models.IntegerField(default=0)

    class Meta:
        db_table = 'amrc_store'
        
    def __str__(self):
        return str(self.name)

class StarOfTheMonth(models.Model):
    
    user = models.ForeignKey(JobUsers, on_delete=models.PROTECT)
    store = models.ForeignKey(Store, on_delete=models.PROTECT,null=True)
    title = models.CharField(max_length=255)
    # award_lebel = models.IntegerField(choices=AWARD_CHOICES)
    # selected_date = models.DateField(auto_now_add=False, blank=True, null=True,validators=[validate_date])
    from_date = models.DateField(auto_now_add=False, blank=True, null=True)
    end_date = models.DateField(auto_now_add=False, blank=True, null=True)
    
    createdAt = models.DateTimeField(default=cust_timezone())
    updatedAt = models.DateTimeField(auto_now_add=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    updated_by = models.IntegerField(default=0)
    brand_id = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'amrc_start_of_the_month'
        
    def __str__(self):
        return str(self.title)

class Points(models.Model):
    
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=250, null=True, blank=True)
    points = models.IntegerField(default=0)
    createdAt = models.DateTimeField(default=cust_timezone())
    updatedAt = models.DateTimeField(auto_now_add=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    updated_by = models.IntegerField(default=0)
    brand_id = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'amrc_points'
        
    def __str__(self):
        return str(self.title)
