from django import forms
from americana.validation import *
from post.models import Posts

class PollsAdminCreationForm(forms.ModelForm):
     
    use_required_attribute = False
    requested_asset = None
    
    title = forms.CharField(label='Question', error_messages={'required' : 'The  Question field is required'})
    description = forms.CharField(label='Description', widget=forms.Textarea, error_messages={'required' : 'The Description field is required'}, validators=[lambda value: alpha_space(value, 100, 'description')])
    
    class Meta:
        model = Posts
        fields = ('title', 'description') 
    
    def __init__(self, *args, **kwargs):
        super(PollsAdminCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder':'Poll Question'})
        self.fields['description'].widget.attrs.update({'class': 'form-control','placeholder':'Description'})
        
    def clean(self):

        cleaned_data  = super(PollsAdminCreationForm, self).clean()
        title = cleaned_data.get('title')
        
        if title != None:
            kwargs = {
                '{0}__{1}'.format('title', 'startswith'): title,
                '{0}__{1}'.format('title', 'endswith'): title
            }
        return self.cleaned_data
