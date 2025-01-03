from django.db import models
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from americana.utils import cust_timezone

# add field in existing group table
Group.add_to_class('status', models.IntegerField(_('status'), default=0))
# '1- Active, 0 - De-active, 2 -Deleted,3 - Locked')
Group.add_to_class('is_deleted', models.IntegerField(default=0))
Group.add_to_class(
                   'createdAt', 
                   models.DateTimeField(_('created At'),
                                        default=cust_timezone()))
Group.add_to_class(
                    'updatedAt',
                    models.DateTimeField(_('last modified'),
                                         auto_now_add=True))
Group.add_to_class(
                    'modified_by',
                    models.IntegerField(_('modified by'), default=0))


class JobRoles(models.Model):
    name = models.CharField(max_length=100)
    direct_post_publice = models.BooleanField(default=False)
    description = models.TextField(blank=False, verbose_name='Description')
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=cust_timezone())
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    brand_id      = models.IntegerField(default=0)
    ip_address  = models.GenericIPAddressField(blank=True, null=True)
    created_by  = models.IntegerField(default=0)
    updated_by  = models.IntegerField(default=0)

    class Meta:
        db_table = 'amrc_job_roles'
        
    def __str__(self):
        return str(self.name)
