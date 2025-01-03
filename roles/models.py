from django.db import models

from django.contrib.auth.models import Group

from django.contrib.auth.models import PermissionsMixin, AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

# ~ Group.add_to_class('status', models.IntegerField(_('status'), default=0)) #'1- Active, 0 - De-active, 2 -Deleted,3 - Locked')
# ~ Group.add_to_class('is_deleted', models.IntegerField(default=0))
# ~ Group.add_to_class('createdat', models.DateTimeField(_('created at'), default=timezone.now))
# ~ Group.add_to_class('updatedat', models.DateTimeField(_('last modified'), auto_now_add=True))
# ~ Group.add_to_class('modified_by', models.IntegerField(_('modified by'), default=0))

    
