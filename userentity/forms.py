from django import forms
from .models import *
from americana.validation import *
from .models import UserEntity

class UserEntityAdminCreationForm(forms.ModelForm):
     
    use_required_attribute = False
    requested_asset        = None
    
    name        = forms.CharField(label='Name', max_length=50, min_length=2, error_messages={'required' : 'The name field is required'}, validators=[lambda value: valid_name(value, 10, 'name')])
    description = forms.CharField(label='Description', widget=forms.Textarea, error_messages={'required' : 'The description field is required'}, validators=[lambda value: alpha_space(value, 100, 'description')])
        
    class Meta:
        model  = UserEntity
        fields = ('name', 'description')
    
    def __init__(self, *args, **kwargs):
        # ~ self.enterprise_id = kwargs.pop("enterprise_id")
        if 'group_id' in kwargs:
            self.group_id = kwargs.pop("group_id")
        else:
            self.group_id = 0
        super(UserEntityAdminCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Name'})
        self.fields['description'].widget.attrs.update({'class': 'form-control','placeholder':'Description'})
        # self.fields['enterprise'].widget.attrs.update({'class': 'form-control','placeholder':'Enterprise'})
       
    
    def clean(self):

        cleaned_data  = super(UserEntityAdminCreationForm, self).clean()
        # ~ enterprise_id = self.enterprise_id
        # used for update group for unique check
        group_id      = self.group_id
        name          = cleaned_data.get('name')
        
        if name != None:
            kwargs = {
                '{0}__{1}'.format('name', 'startswith'): name,
                '{0}__{1}'.format('name', 'endswith'): name
            }
            if group_id:
                obj = UserEntity.objects.exclude(id=group_id).filter(**kwargs).exists()
            else:    
                obj = UserEntity.objects.filter(**kwargs).exists()
            if obj:
                self.add_error('name', 'Name is already exists, please try another')
            
        return self.cleaned_data
