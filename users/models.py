from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from americana.utils import cust_timezone
from .UserManager import UserManager
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.conf import settings

class User(AbstractBaseUser, PermissionsMixin):

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,10}$',
        message="Phone number must be entered 10 digits valid phone no.")

    username = models.CharField(
        max_length=50, default='', blank=True, null=True)
    email = models.EmailField(_('email id'), max_length=80, unique=True)
    phone = models.CharField(
        validators=[phone_regex], max_length=10, unique=True)
    name = models.CharField(_('name'), max_length=30, blank=True)
    slug = models.SlugField(max_length=250, null=True, blank=True)
    user_type = models.CharField(max_length=50, blank=True, null=True)
    password_attempt = models.IntegerField(_('password attempt'), default=0)
    status = models.IntegerField(_('status'), default=0)
    # '1-Active, 0-De-active, 2-Deleted, 3-Locked')
    createdAt = models.DateTimeField(_('created at'), default=cust_timezone())
    last_modified = models.DateTimeField(_('last modified'), auto_now=True)
    last_login_json = models.JSONField(blank=True, null=True)
    
    created_by = models.IntegerField(default=0)
    modified_by = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    is_active = models.BooleanField(_('active'), default=False)
    staff = models.BooleanField(default=False)  # staff user non superuser
    admin = models.BooleanField(default=False)  # superuser
    profile_img = models.ImageField(upload_to='profile/', null=True, blank=True)
    is_deleted = models.IntegerField(_('is deleted'), default=0)
    user_logo = models.ImageField(
        upload_to=str(settings.BASE_URL)+"/media/users/logo", null=True, blank=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'amrc_users'
        verbose_name = _('user')
        verbose_name_plural = _('users')
       
    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        # ~ full_name = '%s %s' % (self.first_name, self.last_name)
        full_name = '%s %s' % (self.name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def is_staff(self):
        if self.is_admin:
            return True
        return self.staff

    @property
    def is_admin(self):
        return self.admin


class User_Login_Log(models.Model):

    user_id = models.IntegerField(default=0)
    brand_id = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    login_time = models.DateTimeField(default=cust_timezone())
    createdAt = models.DateTimeField(default=cust_timezone())

    class Meta():
        db_table = 'amrc_user_login_log'
        default_permissions = ()
