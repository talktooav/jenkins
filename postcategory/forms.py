from django import forms
from americana.validation import *
from .models import PostCategory

class PostCategoryAdminCreationForm(forms.ModelForm):
     
    use_required_attribute = False
    requested_asset        = None
    
    name        = forms.CharField(label='Name', max_length=50, min_length=2, error_messages={'required' : 'The category name field is required'})
    description = forms.CharField(label='Description', widget=forms.Textarea, error_messages={'required' : 'The description field is required'}, validators=[lambda value: alpha_space(value, 100, 'description')])
    sequence = forms.IntegerField(label='Sequence', error_messages={'required' : 'The Sequence field is required'})

    class Meta:
        model  = PostCategory
        fields = ('name', 'description','sequence') 
    
    def __init__(self, *args, **kwargs):
        # ~ self.enterprise_id = kwargs.pop("enterprise_id")
        if 'group_id' in kwargs:
            self.group_id = kwargs.pop("group_id")
        else:
            self.group_id = 0
        super(PostCategoryAdminCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Name'})
        self.fields['description'].widget.attrs.update({'class': 'form-control','placeholder':'Description'})
        self.fields['sequence'].widget.attrs.update({'class': 'form-control','placeholder':'Sequence'}) 
       
    
    def clean(self):

        cleaned_data  = super(PostCategoryAdminCreationForm, self).clean()
        group_id      = self.group_id
        name          = cleaned_data.get('name')
        
        if name != None:
            kwargs = {
                '{0}__{1}'.format('name', 'startswith'): name,
                '{0}__{1}'.format('name', 'endswith'): name
            }
            if group_id:
                obj = PostCategory.objects.exclude(id=group_id).filter(**kwargs).exists()
            else:    
                obj = PostCategory.objects.filter(**kwargs).exists()
            if obj:
                self.add_error('name', 'Category Name is already exists, please try another')
            
        return self.cleaned_data
