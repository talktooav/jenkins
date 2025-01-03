from django import forms
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.models import Group
from americana.validation import *
from django.forms.widgets import FileInput
from django.core.validators import FileExtensionValidator
from .models import User
from django.core.files.images import get_image_dimensions
from americana.encryption import decrypt
from americana.utils import timezones


class UserRegisterForm(forms.ModelForm):

    use_required_attribute = False
    requested_asset = None

    name = forms.CharField(
        label='Name', max_length=50, min_length=2,
        error_messages={'required': 'The name field is required.'},
        widget=forms.TextInput,
        validators=[lambda value: valid_name(value, 50, 'name')])
    email = forms.CharField(
        label='Email Id', max_length=50,
        error_messages={'required': 'The email id field is required.'},
        widget=forms.TextInput,
        validators=[lambda value: valid_email(value, 'Email Id')])
    groups = forms.ModelChoiceField(
        label='Role',
        error_messages={'required': 'The role field is required.'},
        widget=forms.Select,
        queryset=Group.objects.exclude(name='Admin').filter(is_deleted=0))
    phone = forms.CharField(
        label='Mobile No.', max_length=10,
        # ~ required = False,
        error_messages={'required': 'The mobile no field is required.'},
        widget=forms.TextInput,
    )
    password1 = forms.CharField(
        label='Password', max_length=15,
        error_messages={'required': 'The password field is required.'},
        help_text='The password must contain one uppercase, one lowercase, \
        one special character and one number and \
        6 to 15 characters in length.',
        widget=forms.PasswordInput,
        validators=[lambda value: valid_password(value, 'password')])
    password2 = forms.CharField(
        label='Confirm Password', max_length=15,
        error_messages={'required': 'The confirm password field is required.'},
        widget=forms.PasswordInput)
    user_logo = forms.ImageField(
        widget=FileInput,
        help_text='Logo image accept only jpeg, jpg, png \
        extention and maximam 400kb size and 400h*400w dimension',
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'png', 'JPG', 'jpeg', 'JPEG', 'PNG'])],
        required=False)

    class Meta:
        model = User
        fields = ('name', 'email', 'phone', 'groups')

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop("created_by")
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['user_logo'].widget.attrs.update({
            'hight': '100', 'width': '150'})
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control input-lg'})
        self.fields['groups'].queryset = Group.objects.filter(
            is_deleted=0).exclude(name='Admin')

    def clean(self):
        groups = self.cleaned_data.get("groups")
        email = self.cleaned_data.get("email")
        
        user_logo = self.cleaned_data.get("user_logo")
        size = 1024*20
        
        if email != None:
            kwargs = {
                '{0}__{1}'.format('email', 'startswith'): email,
                '{0}__{1}'.format('email', 'endswith'): email
            }
            obj = User.objects.filter(**kwargs).values('id', 'email')
            if obj.exists():
                self.add_error('email', 'Email id is already exists, please try another')
                
        # if user_logo:

        #     w, h = get_image_dimensions(user_logo)
        #     width_between = 150 <= w <= 200
        #     height_between = 40 <= h <= 80
        #     if not width_between or not height_between:
        #         self.add_error('user_logo',
        #                        'Logo should be in given dimension.')
        #     if user_logo and size < user_logo.size:
        #         self.add_error('user_logo',
        #                        'Logo exceeds the maximum allowed size of 20kb')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password does not match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        # ~ user.staff     = True
        user.is_active = True
        if commit:
            user.save()
        return user
        # return redirect('user/')


class UserAdminChangeForm(forms.Form):
    requested_asset = None
    use_required_attribute = False

    name = forms.CharField(
        label='Name', max_length=50, min_length=2,
        error_messages={'required': 'The name field is required.'},
        widget=forms.TextInput,
        validators=[lambda value: valid_name(value, 50, 'name')])
    email = forms.CharField(
        label='Email Id', max_length=50,
        error_messages={'required': 'The email id field is required.'},
        widget=forms.TextInput,
        validators=[lambda value: valid_email(value, 'Email Id')])
    phone = forms.CharField(
        label='Mobile No.', max_length=10,
        error_messages={'required': 'The mobile no field is required.'},
        widget=forms.TextInput,
    )
    groups = forms.ModelChoiceField(
        label='Role',
        error_messages={'required': 'The role field is required.'},
        widget=forms.Select, queryset=Group.objects.filter(
            is_deleted=0).exclude(name='Admin'))
    password1 = forms.CharField(
        label='Password', max_length=15,
        error_messages={'required': 'The password field is required.'},
        help_text='The password must contain one uppercase, one lowercase, \
        one special character and one number and \
        6 to 15 characters in length.',
        widget=forms.PasswordInput,
        validators=[lambda value: valid_password(value, 'password')])
    password2 = forms.CharField(
        label='Confirm Password', max_length=15,
        error_messages={'required': 'The confirm password field is required.'},
        widget=forms.PasswordInput)
    user_logo = forms.ImageField(
        label='Brand Logo',
        widget=FileInput,
        validators=[FileExtensionValidator(
                allowed_extensions=['jpg', 'png', 'JPG',
                                    'jpeg', 'JPEG', 'PNG'])],
        required=False)
    user = forms.CharField(widget=forms.HiddenInput, label='')
    filename = forms.CharField(widget=forms.HiddenInput, label='')

    class Meta:
        model = User
        fields = ('name', 'email', 'phone', 'groups')

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop("created_by")
        super(UserAdminChangeForm, self).__init__(*args, **kwargs)
        self.fields['user_logo'].widget.attrs.update({
            'hight': '100', 'width': '150'})
        self.fields['groups'].queryset = Group.objects.filter(is_deleted=0).exclude(name='Admin')
        self.fields['email'].widget.attrs['readonly'] = True

        for field_name, field in self.fields.items():
            if field_name == 'filename' or field_name == 'password1' \
                    or field_name == 'password2':
                field.required = False
        self.fields['name'].widget.attrs.update({
            'class': 'form-control input-lg'})
        self.fields['email'].widget.attrs.update({
            'class': 'form-control input-lg'})
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control input-lg'})
        self.fields['groups'].widget.attrs.update({
            'class': 'form-control input-lg'})
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control input-lg'})
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control input-lg'})

    def clean(self):
        cleaned_data = super(UserAdminChangeForm, self).clean()
        email = cleaned_data.get('email')
        user_logo = cleaned_data.get('user_logo')
        groups = cleaned_data.get('groups')
        user_id = decrypt(cleaned_data.get('user'))

        # ~ if groups and groups.name=='Enterprise':
        if groups:
            size = 1024*20
            if user_logo:
                w, h = get_image_dimensions(user_logo)
                width_between = 150 <= w <= 200
                height_between = 40 <= h <= 60

                # if not width_between or not height_between:
                #     self.add_error(
                #         'user_logo',
                #         'Logo should be in given dimension.')
                # # ~ if h > 400 or w > 400:
                #     # ~ self.add_error('enterprise_logo',
                #     # 'Logo dimension accept only 400h*400w')
                # if size < user_logo.size:
                #     self.add_error(
                #         'user_logo',
                #         'Logo exceeds the maximum allowed size of 20kb.')
            else:
                pass

        if email:
            kwargs = {
                '{0}__{1}'.format('email', 'startswith'): email,
                '{0}__{1}'.format('email', 'endswith'): email
            }
            obj = User.objects.exclude(id=user_id).filter(**kwargs).values(
                'id', 'email')
            # ~ print('obj_query', obj.query)
            if obj.exists():
                self.add_error(
                    'email', 'Email id is already exists, please try another')

        return self.cleaned_data

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and not password2:
            raise forms.ValidationError(
                "The confirm password field is required")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "The confirm password does not match to password.")
        return password2


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email', min_length=2,
        max_length=50,
        error_messages={'required': 'The email id field is required.'},)
    password = forms.CharField(
            widget=forms.PasswordInput,
            error_messages={'required': 'The password field is required.'},)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        request = self.request
        data = self.cleaned_data
        email = data.get("email")
        password = data.get("password")
        qs = User.objects.filter(email=email, is_deleted=0)
        if qs:
            # user email is registered, check active/
            if not qs[0].is_active:
                # not active, check email activation
                # ~ link = reverse("users:resend-activation")
                # ~ reconfirm_msg = """Go to <a href='{resend_link}'>
                # ~ resend confirmation email</a>.
                # ~ """.format(resend_link = link)

                is_confirmable = False
                if is_confirmable:
                    msg1 = "Please check your email to \
                    confirm your account or " + reconfirm_msg.lower()
                    raise forms.ValidationError(mark_safe(msg1))
                email_confirm_exists = False
                if email_confirm_exists:
                    msg2 = "Email not confirmed. " + reconfirm_msg
                    raise forms.ValidationError(mark_safe(msg2))
                if not is_confirmable and not email_confirm_exists:
                    raise forms.ValidationError("This user is inactive.")
        user = authenticate(request, username=email, password=password)
        if user is None or not qs:
            raise forms.ValidationError("Invalid credentials")
        qs.update(last_modified=timezones())
        login(request, user)
        self.user = user
        return data

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control input-lg'})    


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput, required=False)

    use_required_attribute = False
    old_password_flag = True

    def __init__(self, *args, **kwargs):
        self.user_role = kwargs.pop("user_role")

        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def set_old_password_flag(self):
        self.old_password_flag = False
        return 0

    def cleaned_old_password(self, *args, **kwargs):
        old_password = self.cleaned_data.get('old_password')

        if not old_password:
            raise forms.ValidationError("You must enter old password.")
        if not self.old_password_flag:
            raise forms.ValidationError(
                "The old password that you have entered is wrong.")

        return old_password

    def clean(self):
        old_password = self.cleaned_data.get('old_password')
        new_password = self.cleaned_data.get('new_password')
        confirm_new_password = self.cleaned_data.get('confirm_new_password')
        if new_password and new_password != confirm_new_password:
            self.add_error(
                'confirm_new_password',
                "The confirm password does not match to password.")
        if not self.user_role and not old_password:
            self.add_error(
                'old_password', "This field is required.")
        if new_password and old_password and new_password == old_password:
            raise forms.ValidationError(
                'Password must be different from old password.')
        return self.cleaned_data
