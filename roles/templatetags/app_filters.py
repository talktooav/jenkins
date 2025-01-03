import json
from americana.encryption import encrypt, decrypt
from jobusers.models import JobUsers
from americana.constants import APPROVE_STATUS_CHOICES, CHOICES, PUSH_STATUS, POST_LANGUAGE
from django.db.models import Q
from django import template
register = template.Library()

@register.filter()
def to_encrypt(value):
    return str(encrypt(value))

@register.filter()
def to_decrypt(value):
    return decrypt(value)

@register.filter(name='str_replace')
def str_replace(count, string):
    return string.rsplit('/', count)[0]

@register.filter(name='replace_tag')
def replace_tag(tag, value):
    return value.replace(tag, " ")

@register.filter(name='approve_status')
def approve_status(key):
    dict_appv = dict(APPROVE_STATUS_CHOICES)
    return dict_appv[key]

@register.filter(name='status')
def status(key):
    dict_status = dict(CHOICES)
    return dict_status[key]

@register.filter(name='get_count')
def get_count(key):
    if key:
        ret_val = len(key)
    else:
        ret_val = 0
    return ret_val

@register.filter(name='rangee')
def rangee(key):
    start = key
    val = ''
    for i in range(start, 8):
        val = val+str(i)
    return val

@register.filter(name='push_status')
def push_status(key):    
    dict_status = dict(PUSH_STATUS)
    return dict_status[key]

@register.filter(name='get_lang')
def get_lang(key):    
    dict_status = dict(POST_LANGUAGE)
    return dict_status[key]

@register.filter(name='show_options')
def show_options(key):
    # ~ data  = json.loads(key)
    # ~ data  = json.dumps(key)
    data = json.loads(key)
    ret_val = ''
    for dicn in data:
        dic_val = dicn['label']
        ret_val = ret_val+dic_val+', '
    return ret_val

@register.filter(name='getTaggedUsers')
def getTaggedUsers(key):
    users = ''
    if key:
        key = key.split(',')
        for userId in key:
            if userId:
                mod_obj = JobUsers.objects.filter(
                    Q(id=userId)).values('employee_name')[0]
                users = users + str(mod_obj['employee_name']) + ', '
    return users
