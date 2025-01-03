from django import forms
from americana.validation import *
from .models import Posts
from jobusers.models import JobUsers
from postcategory.models import PostCategory
from django.forms.widgets import FileInput
from django.core.validators import FileExtensionValidator
from americana.constants import CHOICES, CHOICESS,POST_LANGUAGE, APPROVE_STATUS_CHOICES, FILE__TYPE_CHOICES


class PostsAdminCreationForm(forms.ModelForm):
     
    use_required_attribute = False
    requested_asset = None
    
    english_title = forms.CharField(label='Title (English)', required=False)
    arabic_title = forms.CharField(label='Title (Arabic)', required=False)
    english_description = forms.CharField(label='Description (English)', required=False, widget=forms.Textarea)
    arabic_description = forms.CharField(label='Description (Arabic)', required=False, widget=forms.Textarea)
    post_category = forms.ModelChoiceField(queryset=PostCategory.objects.filter(is_deleted = False), required=False)
    approve_status = forms.ChoiceField(choices=APPROVE_STATUS_CHOICES)
    file_type = forms.ChoiceField(choices=FILE__TYPE_CHOICES)
    # ~ upldFile = forms.FileField(label='Upload Image/File', allow_empty_file=True, widget=FileInput, required=False, validators=[FileExtensionValidator(allowed_extensions=['jpeg', 'png', 'jpg', 'gif', 'mp4', 'pdf', 'docx', 'xlsx', 'csv', 'text', 'txt', 'xls', 'doc', 'odt', 'pptx', 'zip', 'rar', 'xlsm', 'xlsb', 'xlt', 'xml', 'mp3', 'mp4'])])
    upldFile = forms.FileField(label='Upload Image/File', allow_empty_file=True, widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False, validators=[FileExtensionValidator(allowed_extensions=['jpeg', 'png', 'jpg', 'gif', 'mp4', 'pdf', 'docx', 'xlsx', 'csv', 'text', 'txt', 'xls', 'doc', 'odt', 'pptx', 'zip', 'rar', 'xlsm', 'xlsb', 'xlt', 'xml', 'mp3', 'mp4'])])
    
    
    class Meta:
        model  = Posts
        fields = ('post_category',) 
        
    def __init__(self, *args, **kwargs):
        if 'group_id' in kwargs:
            self.group_id = kwargs.pop("group_id")
        else:
            self.group_id = 0
        
        
        super(PostsAdminCreationForm, self).__init__(*args, **kwargs)
        # ~ for field in self.fields:
            # ~ self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['english_title'].widget.attrs.update({'class': 'form-control', 'placeholder':'Post Title in English'})
        self.fields['arabic_title'].widget.attrs.update({'class': 'form-control', 'placeholder':'Post Title in Arabic'})
        self.fields['english_description'].widget.attrs.update({'class': 'form-control','placeholder':'Description in English'})
        self.fields['arabic_description'].widget.attrs.update({'class': 'form-control','placeholder':'Description in Arabic'})
        
        self.fields['post_category'].widget.attrs.update({'class': 'form-control','placeholder':'Enter Category'})

        # ~ self.fields['post_language'].widget.attrs.update({'class': 'form-control','placeholder':'Select Language'})
        self.fields['approve_status'].widget.attrs.update({'class': 'form-control','placeholder':'Select Status'})
        self.fields['file_type'].widget.attrs.update({'class': 'form-control','placeholder':'Select file type'})
    
           
    def clean(self):

        cleaned_data = super(PostsAdminCreationForm, self).clean()
        
        # used for update group for unique check
        group_id = self.group_id
        english_title = cleaned_data.get('english_title')
        arabic_title = cleaned_data.get('arabic_title')
        arabic_description = cleaned_data.get('arabic_description')
        english_description = cleaned_data.get('english_description')
        post_image = cleaned_data.get('post_image')
        upldFile = cleaned_data.get("upldFile", '')
        
        if not english_title:
            if not arabic_title:
                self.add_error('english_title', 'This field is required.')
        
        if not english_description:
            if not arabic_description:
                self.add_error('english_description', 'This field is required.')
        return self.cleaned_data

class PostUpdateForm(forms.ModelForm):
     
    use_required_attribute = False
    requested_asset = None
    
    english_title = forms.CharField(label='Title (English)', required=False)
    arabic_title = forms.CharField(label='Title (Arabic)', required=False)
    english_description = forms.CharField(label='Description (English)', required=False, widget=forms.Textarea)
    arabic_description = forms.CharField(label='Description (Arabic)', required=False, widget=forms.Textarea)
    post_category = forms.ModelChoiceField(queryset=PostCategory.objects.filter(is_deleted = False), required=False)
    approve_status = forms.ChoiceField(choices=APPROVE_STATUS_CHOICES)
    
    class Meta:
        model  = Posts
        fields = ('post_category',) 
        
    def __init__(self, *args, **kwargs):
        if 'group_id' in kwargs:
            self.group_id = kwargs.pop("group_id")
        else:
            self.group_id = 0
        
        
        super(PostUpdateForm, self).__init__(*args, **kwargs)
        # ~ for field in self.fields:
            # ~ self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['english_title'].widget.attrs.update({'class': 'form-control', 'placeholder':'Post Title in English'})
        self.fields['arabic_title'].widget.attrs.update({'class': 'form-control', 'placeholder':'Post Title in Arabic'})
        self.fields['english_description'].widget.attrs.update({'class': 'form-control','placeholder':'Description in English'})
        self.fields['arabic_description'].widget.attrs.update({'class': 'form-control','placeholder':'Description in Arabic'})
        
        self.fields['post_category'].widget.attrs.update({'class': 'form-control','placeholder':'Enter Category'})

        self.fields['approve_status'].widget.attrs.update({'class': 'form-control','placeholder':'Select Status'})
           
    def clean(self):

        cleaned_data = super(PostUpdateForm, self).clean()
        
        # used for update group for unique check
        group_id = self.group_id
        english_title = cleaned_data.get('english_title')
        arabic_title = cleaned_data.get('arabic_title')
        arabic_description = cleaned_data.get('arabic_description')
        english_description = cleaned_data.get('english_description')
        
        if not english_title:
            if not arabic_title:
                self.add_error('english_title', 'This field is required.')
        
        if not english_description:
            if not arabic_description:
                self.add_error('english_description', 'This field is required.')
        return self.cleaned_data
