import os
import random
import string
from django.utils import timezone
from django.utils.text import slugify
from itertools import chain
import requests
import json


from datetime import datetime, timedelta

def timezones():
    return timezone.now()

def cust_timezone():
    return timezone.now

def epoch_to_timezone(val):
    if val:
        return datetime.fromtimestamp(int(val) / 1000)        
    else:
        return False
        
def get_last_month_data(today):
    '''
    Simple method to get the datetime objects for the 
    start and end of last month. 
    '''
    this_month_start = datetime(today.year, today.month, 1)
    last_month_end = this_month_start - timedelta(days=1)
    last_month_start = datetime(last_month_end.year, last_month_end.month, 1)
    return (last_month_start, last_month_end)


def get_month_data_range(months_ago=1, include_this_month=False):
    '''
    A method that generates a list of dictionaires 
    that describe any given amout of monthly data.
    '''
    today  = datetime.now().today()
    dates_ = []
    if include_this_month:
        # get next month's data with:
        next_month = today.replace(day=28) + timedelta(days=4)
        # use next month's data to get this month's data breakdown
        start, end = get_last_month_data(next_month)
        dates_.insert(0, {
            "start": start.timestamp(),
            "end": end.timestamp(),
            "start_json": start.isoformat(),
            "end": end.timestamp(),
            "end_json": end.isoformat(),
            "timesince": 0,
            "year": start.year,
            "month": str(start.strftime("%B")),
            })
    for x in range(0, months_ago):
        start, end = get_last_month_data(today)
        today = start
        dates_.insert(0, {
            "start": start.timestamp(),
            "start_json": start.isoformat(),
            "end": end.timestamp(),
            "end_json": end.isoformat(),
            "timesince": int((datetime.now() - end).total_seconds()),
            "year": start.year,
            "month": str(start.strftime("%B"))
        })
    #dates_.reverse()
    return dates_ 


def get_filename(path): #/abc/filename.mp4
    return os.path.basename(path)


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_key_generator(instance):
    
    size = random.randint(30, 45)
    key = random_string_generator(size=size)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(key=key).exists()
    if qs_exists:
        return unique_slug_generator(instance)
    return key


def unique_order_id_generator(instance):
    """
    This is for a Django project with an order_id field
    """
    order_new_id = random_string_generator()

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(order_id=order_new_id).exists()
    if qs_exists:
        return unique_slug_generator(instance)
    return order_new_id



def unique_slug_generator(Klass, new_slug=None, exist_id=False):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = slugify(new_slug)
    else:
        slug = slugify(new_slug)
    
    if exist_id:
        qs_exists = Klass.objects.filter(slug=slug).exclude(id=exist_id).exists()
    else:
        qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
                    slug=slug,
                    randstr=random_string_generator(size=4)
                )
        return unique_slug_generator(Klass, new_slug=new_slug)
    return slug
    
def model_to_dict(instance, fields=None, exclude=None):
    """
    Return a dict containing the data in ``instance`` suitable for passing as
    a Form's ``initial`` keyword argument.
    ``fields`` is an optional list of field names. If provided, return only the
    named.
    ``exclude`` is an optional list of field names. If provided, exclude the
    named from the returned dict, even if they are listed in the ``fields``
    argument.
    """
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if not getattr(f, 'editable', False):
            continue
        if fields is not None and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        data[f.name] = f.value_from_object(instance)
    return data

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
    
def session_dict(request):
    if request.session.items():
        return dict(request.session.items())
    else:
        return False    
        

        
def send_push_notification(payload):
    url = 'https://fcm.googleapis.com/fcm/send'
    headers = {"content-type":"application/json", "Authorization":'key=AAAAK_xxQJc:APA91bFA_2WpUCEh3ZsBn3Dd4uRqY1e__uaWswsLIpmSLyIMX_KoQFrN2bP5i5WfnJtlIvi74amqJ2Qz0RozofgclqH3vJ-Us67aWq6f1YFsKHyIXbALQSeQiN-gkHWpodG1Vtq9tNxc'}
    
    # ~ request.add_header("Content-Type", "application/json") #Header, Value                                        
    # ~ request.add_header("Content-Type", "application/json") #Header, Value 
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response
    

