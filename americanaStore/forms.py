from django import forms
from americana.validation import *
from .models import Products
from django.forms.widgets import FileInput
from django.core.validators import FileExtensionValidator

class ProductAdminCreationForm(forms.ModelForm):
     
    use_required_attribute = False
    requested_asset        = None
    
    name = forms.CharField(label='Name', max_length=50, min_length=2, error_messages={'required' : 'The name field is required'})
    description = forms.CharField(label='Description', widget=forms.Textarea, error_messages={'required' : 'The Description field is required'})
    price = forms.IntegerField(label='Price', error_messages={'required' : 'The Price field is required'})
    upldFile = forms.FileField(label='Upload Image/File', allow_empty_file=True, widget=FileInput, required=False, validators=[FileExtensionValidator(allowed_extensions=['jpeg', 'png', 'jpg', 'gif', 'mp4', 'pdf', 'docx', 'xlsx', 'csv', 'text', 'txt', 'xls', 'doc', 'odt', 'pptx', 'HTML', 'HTM', 'RTF', 'bmp', 'pub', 'tiff', 'psd', 'dwg', 'xbm', 'xpm', 'zip', 'rar', 'accdb', 'xltm', 'xlsm', 'xlsb', 'xlt', 'xml', 'avi', 'mp3', 'flac', 'mp4', 'wav', 'aac', 'wma', 'mkv'])])
    
    class Meta:
        model  = Products
        fields = ('name', 'description', 'price') 
    
    def __init__(self, *args, **kwargs):
        if 'group_id' in kwargs:
            self.group_id = kwargs.pop("group_id")
        else:
            self.group_id = 0
        super(ProductAdminCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Post Title'})
        self.fields['description'].widget.attrs.update({'class': 'form-control','placeholder':'Description'})
        
        self.fields['price'].widget.attrs.update({'class': 'form-control','placeholder':'Enter Price'})
        
       
    
    def clean(self):

        cleaned_data  = super(ProductAdminCreationForm, self).clean()
        
        # used for update group for unique check
        group_id = self.group_id
        title = cleaned_data.get('name')
        product_image = cleaned_data.get('product_image')
        
        if title != None:
            kwargs = {
                '{0}__{1}'.format('title', 'startswith'): title,
                '{0}__{1}'.format('title', 'endswith'): title
            }
        return self.cleaned_data