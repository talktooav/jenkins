from django import forms
from .models import *
from post.models import Posts
from americana.validation import *
from americana.constants import CHOICES, CHOICESS


class PostsAdminCreationForm(forms.ModelForm):
     
    use_required_attribute = False
    requested_asset        = None
    
    title        = forms.CharField(label='Title', max_length=50, min_length=2, error_messages={'required' : 'The  title field is required'}, validators=[lambda value: valid_name(value, 10, 'title')])
    description  = forms.CharField(label='Description', widget=forms.Textarea, error_messages={'required' : 'The Description field is required'}, validators=[lambda value: alpha_space(value, 100, 'description')])
    status = forms.ChoiceField(choices=CHOICES)
    
    class Meta:
        model  = Posts
        fields = ('title', 'description','post_type','user_id','post_category','post_image','post_file','file_type','taggedusers','like_count','comment_count','approve_status','status') 
    
    def __init__(self, *args, **kwargs):
        if 'group_id' in kwargs:
            self.group_id = kwargs.pop("group_id")
        else:
            self.group_id = 0
        super(PostsAdminCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Post Title'})
        self.fields['description'].widget.attrs.update({'class': 'form-control','placeholder':'Description'})
        self.fields['post_type'].widget.attrs.update({'class': 'form-control','placeholder':'Enter Your Permission Policy'})
        self.fields['user_id'].widget.attrs.update({'class': 'form-control','placeholder':'Select User'})
        self.fields['post_category'].widget.attrs.update({'class': 'form-control','placeholder':'Enter Category'})
        self.fields['post_image'].widget.attrs.update({'class': 'form-control','placeholder':'Enter Your Permission Policy'})
        self.fields['post_file'].widget.attrs.update({'class': 'form-control','placeholder':'Enter Post image'})
        self.fields['file_type'].widget.attrs.update({'class': 'form-control','placeholder':'Select file type'})
        self.fields['taggedusers'].widget.attrs.update({'class': 'form-control','placeholder':'Enter taggeduser comma seprated'})
        self.fields['like_count'].widget.attrs.update({'class': 'form-control','placeholder':'Enter like count'})
        self.fields['comment_count'].widget.attrs.update({'class': 'form-control','placeholder':'Enter comment count'})
        self.fields['approve_status'].widget.attrs.update({'class': 'form-control','placeholder':'Select Status'})
        
    def clean(self):

        cleaned_data  = super(PostsAdminCreationForm, self).clean()
        # used for update post for unique check
        group_id      = self.group_id
        title          = cleaned_data.get('title')
        post_image          = cleaned_data.get('post_image')
        
        if title != None:
            kwargs = {
                '{0}__{1}'.format('title', 'startswith'): title,
                '{0}__{1}'.format('title', 'endswith'): title
            }
            if group_id:
                obj = Posts.objects.exclude(id=group_id).filter(**kwargs).exists()
            else:    
                obj = Posts.objects.filter(**kwargs).exists()
            if obj:
                self.add_error('title', 'Category Name is already exists, please try another')
            
        return self.cleaned_data
