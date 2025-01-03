from django import forms
from .models import *
from americana.validation import *
from jobusers.models import JobUsers
from rewards.models import Store

class StoresAdminCreationForm(forms.ModelForm):
     
    use_required_attribute = False
    requested_asset = None
    
    name = forms.CharField(label='Name', max_length=100, min_length=2, error_messages={'required' : 'The store name field is required'})
    store_id = forms.CharField(label='Store_id', max_length=10, error_messages={'required' : 'The Store Id field is required'})
    
    class Meta:
        model = Store
        fields = ('name', 'store_id')
    
    def __init__(self, *args, **kwargs):
        
        super(StoresAdminCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'maxlength': '255', 'placeholder':'Store Name'})
        self.fields['store_id'].widget.attrs.update({'class': 'form-control','placeholder':'Store Id', 'min' : 0})
        
    def clean(self):
        cleaned_data = super(StoresAdminCreationForm, self).clean()
        title = cleaned_data.get('name')
        store_id = cleaned_data.get('store_id')
        
        # if title != None:
            # if self.point_id:
            # obj = Store.objects.exclude(id=self.point_id).filter(store_id=store_id).values('id')
            # if obj.exists():
            #     self.add_error('name', 'This Store already exists, please try another')   
        return self.cleaned_data


class RewardsAdminCreationForm(forms.ModelForm):
     
    use_required_attribute = False
    requested_asset = None
    
    title = forms.CharField(label='Title', max_length=50, min_length=2, error_messages={'required' : 'The title field is required'}, validators=[lambda value: valid_name(value, 10, 'title')])
    user = forms.ModelChoiceField(queryset=JobUsers.objects.filter())
    store = forms.ModelChoiceField(queryset=Store.objects.filter()) 
    from_date = forms.DateField(
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#from_date'
        })
    )
    end_date = forms.DateField(
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#end_date'
        })
    )
    class Meta:
        model = StarOfTheMonth
        fields = ('title', 'store','from_date','end_date' ,'user')
    
    def __init__(self, *args, **kwargs):
        if 'group_id' in kwargs:
            self.group_id = kwargs.pop("group_id")
        else:
            self.group_id = 0
        super(RewardsAdminCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Title'})
        self.fields['from_date'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'End date (YYYY-MM-DD)'})
        self.fields['end_date'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'End date (YYYY-MM-DD)'})
        self.fields['user'].widget.attrs.update({'class': 'form-control','placeholder':'Select User'})
        self.fields['store'].widget.attrs.update({'class': 'form-control','placeholder':'Select Store'})
       
    def clean(self):
        cleaned_data = super(RewardsAdminCreationForm, self).clean()
        # award_lebel = cleaned_data.get('award_lebel')
        # selected_date = cleaned_data.get('selected_date')
        
        # if selected_date != None and award_lebel != None:
        #     obj = StarOfTheMonth.objects.filter(selected_date=selected_date, award_lebel=award_lebel).values('id', 'award_lebel')
        #     if obj.exists():
        #         self.add_error('award_lebel', 'This award is already exists for this month and year, please try another')   
        # return self.cleaned_data


class PointsAdminCreationForm(forms.ModelForm):
     
    use_required_attribute = False
    requested_asset = None
    
    title = forms.CharField(label='Title', max_length=100, min_length=2, error_messages={'required' : 'The title field is required'}, validators=[lambda value: valid_name(value, 10, 'title')])
    points = forms.CharField(label='Points', max_length=10, error_messages={'required' : 'The points field is required'}, validators=[lambda value: check_numeric(value, 10, 'points')])
    
    class Meta:
        model = Points
        fields = ('title', 'points')
    
    def __init__(self, *args, **kwargs):
        if 'point_id' in kwargs:
            self.point_id = kwargs.pop("point_id")
        else:
            self.point_id = 0
        super(PointsAdminCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Title'})
        self.fields['points'].widget.attrs.update({'class': 'form-control','placeholder':'Points', 'min' : 0, 'max' : 3, 'value':0})
        
    def clean(self):
        cleaned_data = super(PointsAdminCreationForm, self).clean()
        title = cleaned_data.get('title')
        points = cleaned_data.get('points')
        
        if title != None:
            if self.point_id:
                obj = Points.objects.exclude(id=self.point_id).filter(title=title).values('id')
                if obj.exists():
                    self.add_error('title', 'This title is already exists, please try another')   
            else:
                obj = Points.objects.filter(title=title).values('id')
                if obj.exists():
                    self.add_error('title', 'This title is already exists, please try another')   
        return self.cleaned_data
