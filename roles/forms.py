from django import forms
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from americana.validation import *
from americana.encryption import decrypt

class RoleCreateForm(forms.ModelForm):
    
    use_required_attribute = False
    name = forms.CharField(label='Name*', widget=forms.TextInput, error_messages={'required': 'The name field is required.'}, validators=[lambda value: valid_name(value, 10, 'name')])
    
    class Meta:
        model  = Group
        fields = ('name', 'permissions')
    
        
class RoleChangeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    name = forms.CharField(label='Name', error_messages={'required': 'The name field is required.'}, widget=forms.TextInput, validators=[lambda value: valid_name(value, 10, 'name')])
    role = forms.CharField(widget=forms.HiddenInput())
    
    def clean(self):
        cleaned_data = super(RoleChangeForm, self).clean()
        name         = cleaned_data.get('name')
        role_id      = decrypt(cleaned_data.get('role'))
        
        if name == '':
             self.add_error('name', 'The name field is required.')
        else:
            group_name = dict(self.data)['name'][0]
            obj        = Group.objects.exclude(id=role_id).filter(name=name, is_deleted=0)
            # ~ print('obj', obj.query)
            if obj:
                self.add_error('name', 'Name is already exist, please try another')
        return self.cleaned_data

    class Meta:
        model  = Group
        fields = ('name', 'permissions')

    
