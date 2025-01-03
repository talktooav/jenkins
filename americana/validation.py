from django import forms
import re
from django.core.exceptions import ValidationError

def check_size(value, length, label):
    if len(str(value)) < length:
        raise forms.ValidationError("The {} is too short.".format(label))
        
def check_type(value, types, label):
    if (type(value) != types):
        raise forms.ValidationError("Please choose valid {}.".format(label))

def check_numeric(value, length, label):
    if (value.isnumeric() != True and len(str(value)) < length):
        raise forms.ValidationError("Please choose valid {}.".format(label))


def valid_email(value, label):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if value == None:
        raise forms.ValidationError("The {} field is required.".format(label))
    elif re.search(regex,value) == None:
        raise forms.ValidationError('Please enter valid {}.'.format(label))
        
def valid_phone(value, label):
    Pattern = re.compile("(0/91)?[7-9][0-9]{9}")
    if Pattern.match(value) ==  None:
        raise forms.ValidationError('Please enter valid {}.'.format(label)) 
            
def valid_name(value, length, label):
    regex    = re.compile("^[a-zA-Z \.\-]{2,50}$")
    validate = regex.search(value)
    if value == None:
        raise forms.ValidationError("The {} field is required.".format(label))
    elif validate == None:
        raise forms.ValidationError("Please enter valid {}.".format(label))
        
def alpha_space(value, length, label):
    check    = re.compile("^[a-zA-Z0-9 @®®™%°*!:;()×+~,_\-&.+:\'\%\()\/\.\-']{0,250}$")
    validate = check.match(str(value)) 
    if validate == None:
        raise forms.ValidationError('Please enter valid {}.'.format(label))
        
def valid_password(value, label):
    regex = re.compile('^(?=\S{6,15}$)(?=.*?\d)(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[^A-Za-z\s0-9])')        
    validate = regex.search(value)
    if value and validate == None:
        raise forms.ValidationError('Please enter valid password.')
    elif value == None:
        raise forms.ValidationError('The {} field is required.'.format(label))    

def valid_range(value, length, label):
    CHECK_RE = re.compile('[a-zA-Z0-9_-]+$')
    if len(value)>length:
        raise forms.ValidationError("Please enter the minimum character{}".format(label))
    if CHECK_RE.match(value)==None:
        raise forms.ValidationError("Please enter only number and character {} ".format(label))

def url_validate(value, length, label):
    check = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    validate = check.match(str(value))
    if validate == None:
        raise forms.ValidationError('Please enter valid {}'.format(label))

def file_validate(file):
    file_size = file.file.size
    print('this is file size getting in file validator :::::::',file_size)
    limit_kb = 150
    if file_size > limit_kb * 1024:
        raise ValidationError("Max size of file is %s KB" % limit_kb)

    #limit_mb = 8
    #if file_size > limit_mb * 1024 * 1024:
    #    raise ValidationError("Max size of file is %s MB" % limit_mb)
def alphaneumeric(value, length, label):
    regex    = re.compile("^[a-zA-Z0-9_]+$")
    validate = regex.search(value)
    if value == None:
        raise forms.ValidationError("The {} field is required.".format(label))
    elif validate == None:
        raise forms.ValidationError("Please enter valid {}.".format(label))
