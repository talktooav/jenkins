from django import forms
from americana.validation import *
from .models import Moderation

class ModerationAdminCreationForm(forms.ModelForm):
     
    use_required_attribute = False
    requested_asset        = None
    
    word        = forms.CharField(label='Word', max_length=50, min_length=2, error_messages={'required' : 'The word field is required'}, validators=[lambda value: valid_name(value, 10, 'word')])
    description = forms.CharField(label='Description', widget=forms.Textarea, error_messages={'required' : 'The description field is required'}, validators=[lambda value: alpha_space(value, 100, 'description')])
        
    class Meta:
        model  = Moderation
        fields = ('word', 'description')
    
    def __init__(self, *args, **kwargs):
        
        if 'group_id' in kwargs:
            self.group_id = kwargs.pop("group_id")
        else:
            self.group_id = 0
        super(ModerationAdminCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['word'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Word'})
        self.fields['description'].widget.attrs.update({'class': 'form-control','placeholder':'Description'})
        # self.fields['enterprise'].widget.attrs.update({'class': 'form-control','placeholder':'Enterprise'})
       
    
    def clean(self):

        cleaned_data  = super(ModerationAdminCreationForm, self).clean()
        group_id      = self.group_id
        name          = cleaned_data.get('name')
        
        if name != None:
            kwargs = {
                '{0}__{1}'.format('word', 'startswith'): name,
                '{0}__{1}'.format('word', 'endswith'): name
            }
            if group_id:
                obj = Moderation.objects.exclude(id=group_id).filter(**kwargs).exists()
            else:    
                obj = Moderation.objects.filter(**kwargs).exists()
            if obj:
                self.add_error('name', 'Name is already exists, please try another')
            
        return self.cleaned_data
