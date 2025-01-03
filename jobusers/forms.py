from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe
from americana.validation import *
from .models import JobUsers
from django.core.files.images import get_image_dimensions
from americana.encryption import decrypt
from americana.utils import timezones
from jobrole.models import JobRoles
from userentity.models import UserEntity
from americana.constants import GENDER_CHOICES, CHOICES

class JobUserRegisterForm(forms.ModelForm):
    
    use_required_attribute = False
    employee_name = forms.CharField(label='Name', max_length=50, min_length=2, error_messages={'required': 'The name field is required.'}, widget=forms.TextInput, validators=[lambda value: valid_name(value, 50, 'name')])
    # ~ phone = forms.CharField(label='Phone', max_length=10, min_length=10, error_messages={'required': 'The phone field is required.'}, widget=forms.TextInput)
    # ~ status = forms.ChoiceField(choices=CHOICES)
    gender = forms.ChoiceField(choices=GENDER_CHOICES)

    market=forms.CharField(label="Market", max_length=50, min_length=2,widget=forms.TextInput)

    # ~ email = forms.CharField(label='Email Id', max_length=50, error_messages={'required': 'The email id field is required.'}, widget=forms.TextInput, validators=[lambda value: valid_email(value, 'Email Id')])
    password = forms.CharField(label='Password', max_length=15, error_messages={'required': 'The password field is required.'}, help_text='The password must contain one uppercase, one lowercase, one special character and one number and 6 to 15 characters in length.', widget=forms.PasswordInput, validators=[lambda value: valid_password(value, 'password')],required=False)
    password2 = forms.CharField(label='Confirm Password', max_length=15, error_messages={'required': 'The confirm password field is required.'}, widget=forms.PasswordInput,required=False)
    date_of_birth = forms.CharField(label='DOB',required=True)
    
    
    class Meta:
        model = JobUsers
        # ~ fields = ('first_name', 'last_name', 'date_of_birth', 'employee_code', 'email', 'phone', 'job_role', 'entity', 'status')
        fields = ('employee_name', 'date_of_birth', 'employee_code', 'job_role', 'entity','market')
    
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 and not password2:
            raise forms.ValidationError("The confirm password field is required")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password does not match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(JobUserRegisterForm, self).save(commit=False)
        # ~ user.set_password(self.cleaned_data["password"])
        # user.staff = True
        user.is_active = True
        if commit:
            user.save()
        return user
       
        
    def __init__(self, *args, **kwargs):
        super(JobUserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['employee_name'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Enter Employee Name'})
        self.fields['date_of_birth'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Enter DOB (YYYY-MM-DD)'})
        self.fields['employee_code'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Enter Employee Id'})
        self.fields['market'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Market'})
        # ~ self.fields['email'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Enter Email'})
        # ~ self.fields['phone'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Enter Phone'})
        self.fields['job_role'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':''})
        self.fields['entity'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':''})
        # ~ self.fields['status'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':''})
        self.fields['gender'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':''})
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class' : 'form-control input-lg'})
        
    def clean(self):

        cleaned_data = super(JobUserRegisterForm, self).clean()
        cleaned_data = self.cleaned_data
        # ~ phone = cleaned_data.get("phone")
        job_role = cleaned_data.get("job_role")
        
        # ~ if not phone:
            # ~ msg = "Phone is required"
            # ~ self._errors["phone"] = self.error_class([msg])
        # ~ if job_role != "admin":
            # ~ msg = "DOB is required"
            # ~ msg1 = "Employee Id is required"
            # ~ self._errors["date_of_birth"] = self.error_class([msg])
            # ~ self._errors["employee_id"] = self.error_class([msg1])
        return self.cleaned_data

        
class JobUserAdminChangeForm(forms.Form):
    requested_asset = None
    
    def __init__(self, *args, **kwargs):
        super(JobUserAdminChangeForm, self).__init__(*args, **kwargs)
            
    use_required_attribute = False
    
    employee_name = forms.CharField(label='Name', max_length=50, min_length=2, error_messages={'required': 'The name field is required.'}, widget=forms.TextInput, validators=[lambda value: valid_name(value, 50, 'name')])
    date_of_birth = forms.CharField(label='DOB',required=True)

    market=forms.CharField(label="Market", max_length=50, min_length=2,widget=forms.TextInput)
    
    employee_code = forms.CharField(label='Employee Code', max_length=30, error_messages={'required': 'The employee code field is required.'})
    # ~ email = forms.CharField(label='Email', max_length=30, error_messages={'required': 'The employee id field is required.'}, validators=[lambda value: valid_email(value, 'email')])
    # ~ phone  = forms.CharField(label='Phone', max_length=10, min_length=10, error_messages={'required': 'The phone field is required.'}, widget=forms.TextInput, validators=[lambda value: valid_phone(value, 'phone')])
    job_role     = forms.ModelChoiceField(label='Role', error_messages={'required': 'The role field is required.'}, widget=forms.Select, queryset=JobRoles.objects.filter(is_deleted = False))
    entity     = forms.ModelChoiceField(label='Entity', error_messages={'required': 'The role field is required.'}, widget=forms.Select, queryset=UserEntity.objects.filter(is_deleted = False))
    # ~ status = forms.ChoiceField(choices=CHOICES)
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    user = forms.CharField(widget=forms.HiddenInput, label='')
    password = forms.CharField(label='Password', max_length=15, error_messages={'required': 'The password field is required.'}, help_text='The password must contain one uppercase, one lowercase, one special character and one number and 6 to 15 characters in length.', widget=forms.PasswordInput, validators=[lambda value: valid_password(value, 'password')],required=False)
    password2 = forms.CharField(label='Confirm Password', max_length=15, error_messages={'required': 'The confirm password field is required.'}, widget=forms.PasswordInput,required=False)
    
    
    def clean(self):
        cleaned_data      = super(JobUserAdminChangeForm, self).clean()
        email             = None #cleaned_data.get('email')
        employee_code     = cleaned_data.get('employee_code')
        # ~ phone             = cleaned_data.get('phone')
        user_id           = decrypt(cleaned_data.get('user'))
        
        if email != None:
            kwargs = {
                '{0}__{1}'.format('email', 'startswith'): email,
                '{0}__{1}'.format('email', 'endswith'): email
            }
            obj = JobUsers.objects.exclude(id=user_id).filter(**kwargs).values('id', 'email')
            # ~ print('obj_query', obj.query)
            if obj.exists():
                self.add_error('email', 'Email id is already exists, please try another')
        
        if employee_code != None:
            obj = JobUsers.objects.exclude(id=user_id).filter(employee_code=employee_code).values('id')
            # ~ print('obj_query', obj.query)
            if obj.exists():
                self.add_error('employee_code', 'Employee code is already exists, please try another')
        
        # ~ if phone != None:
            # ~ obj = JobUsers.objects.exclude(id=user_id).filter(phone=phone).values('id', 'email')
            # ~ if obj.exists():
                # ~ self.add_error('phone', 'Phone number is already exists, please try another')
            
        return self.cleaned_data
	
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 and not password2:
            raise forms.ValidationError("The confirm password field is required")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password does not match.")
        return password2
         
    class Meta:
        model  = JobUsers
        # ~ fields = ('first_name', 'last_name', 'date_of_birth', 'employee_code', 'email', 'phone', 'job_role', 'entity','status')
        fields = ('employee_name', 'date_of_birth', 'employee_code', 'job_role', 'entity')
        
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(JobUserAdminChangeForm, self).save(commit=False)
        # ~ user.set_password(self.cleaned_data["password"])
        # user.staff     = True
        user.is_active = True
        if commit:
            user.save()
        return user
        #return redirect('user/')
        
    def __init__(self, *args, **kwargs):
        super(JobUserAdminChangeForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name == 'filename' or field_name == 'password' or field_name == 'password2':
                field.required = False
        self.fields['employee_name'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Enter Employee Name'})
        self.fields['date_of_birth'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Enter DOB (YYYY-MM-DD)'})
        self.fields['employee_code'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Enter Employee Code'})
        # ~ self.fields['email'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Enter Email'})
        # ~ self.fields['phone'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Enter Phone'})
        self.fields['job_role'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':''})
        self.fields['entity'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':''})
        # ~ self.fields['status'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':''})
        self.fields['gender'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':''})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':''})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':''})
