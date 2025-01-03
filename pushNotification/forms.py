from django import forms
from .models import *
from americana.validation import *
from jobusers.models import JobUsers
from jobrole.models import JobRoles
# ~ from bootstrap_datepicker_plus import DateTimePickerInput

class PushAdminCreationForm(forms.ModelForm):
     
    use_required_attribute = False
    requested_asset        = None
    
    title = forms.CharField(label='Title', max_length=50, min_length=2, error_messages={'required' : 'The  title field is required'}, validators    =[lambda value: valid_name(value, 10, 'title')])
    description = forms.CharField(label='Description', widget=forms.Textarea, error_messages={'required' : 'The Description field is required'}, validators =[lambda value: alpha_space(value, 100, 'description')])
    user = forms.ModelChoiceField(label='User', required=False,queryset=JobUsers.objects.filter(is_active=1))
    job_role = forms.ModelChoiceField(label='Job Roles', required=False, queryset=JobRoles.objects.filter(is_deleted=0))
    link = forms.URLField(label='Link',required=False)
    # ~ schedule_date_time = forms.CharField(label='Schedule Date Time',required=False)

    class Meta:
        model  = PushNotification
        fields = ('title', 'description', 'user', 'job_role', 'link') 
    
    def __init__(self, *args, **kwargs):
        # ~ self.enterprise_id = kwargs.pop("enterprise_id")
        
        super(PushAdminCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Push Title'})
        self.fields['description'].widget.attrs.update({'class': 'form-control','placeholder':'Description'})
        # ~ self.fields['schedule_date_time'].widget.attrs.update({'class': 'form-control','placeholder':'Enter Date time in (YYYY-MM-DD H:i:s)  format'})
    def clean(self):

        cleaned_data  = super(PushAdminCreationForm, self).clean()
        title          = cleaned_data.get('title')
        user_id        = self.cleaned_data.get('user_id') 
        
        cleaned_data = self.cleaned_data
        user = cleaned_data.get("user")
        job_role = cleaned_data.get("job_role")
        schedule_date_time= cleaned_data.get("schedule_date_time")
        schedule_date_time= None

        if title != None:
            kwargs = {
                '{0}__{1}'.format('title', 'startswith'): title,
                '{0}__{1}'.format('title', 'endswith'): title
            }
            
        
        if not user and not job_role:
            msg = "Either choose User or Job Role"
            self._errors["user"] = self.error_class([msg])
            self._errors["job_role"] = self.error_class([msg])

            
        return self.cleaned_data
