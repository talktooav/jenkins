from django import forms
from django.forms.widgets import FileInput
from django.db.models import Q
from django.core.validators import FileExtensionValidator
from americana.validation import *
from americana.utils import timezones
from .models import Quizes, QuizQuestions, QuizResult
from jobusers.models import JobUsers
from postcategory.models import PostCategory
from americana.constants import CHOICES, CHOICESS,POST_LANGUAGE,IMAGECHOICE,APPROVE_STATUS_CHOICES
from americana.encryption import decrypt


class QuizAdminCreationForm(forms.ModelForm):
     
    use_required_attribute = False
    requested_asset = None
    
    name = forms.CharField(label='Name', max_length=50, min_length=2, error_messages={'required' : 'The  title field is required'}, validators=[lambda value: valid_name(value, 10, 'name')])
    status = forms.ChoiceField(choices=CHOICES)
    isimage = forms.ChoiceField(choices=IMAGECHOICE)
    start_date = forms.DateField(
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#start_date'
        })
    )
    end_date = forms.DateField(
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#end_date'
        })
    )
    result_date = forms.DateField(
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#result_date'
        })
    )
    approve_status = forms.ChoiceField(choices=APPROVE_STATUS_CHOICES)
    
    class Meta:
        model  = Quizes
        fields = ('name', 'start_date', 'end_date', 'result_date') 
        
    
    def __init__(self, *args, **kwargs):
        if 'group_id' in kwargs:
            self.group_id = kwargs.pop("group_id")
        else:
            self.group_id = 0
        super(QuizAdminCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Post Name'})
        self.fields['isimage'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Is it image'})
        self.fields['approve_status'].widget.attrs.update({'class': 'form-control','placeholder':'Select Status'})
        # self.fields['user'].widget.attrs.update({'class': 'form-control','placeholder':'Select User'})
        self.fields['start_date'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Start date (YYYY-MM-DD)'})
        self.fields['end_date'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'End date (YYYY-MM-DD)'})
        self.fields['result_date'].widget.attrs.update({'class': 'form-control', 'maxlength': '50', 'placeholder':'Result date (YYYY-MM-DD)'})
    
    def clean(self): 
        
        # data from the form is fetched using super function 
        super(QuizAdminCreationForm, self).clean() 
        
        start_date = self.cleaned_data.get('start_date') 
        end_date = self.cleaned_data.get('end_date') 
        result_date = self.cleaned_data.get('result_date') 
               
        if start_date:
            pass
            # ~ if start_date < timezones().date(): 
                # ~ self._errors['start_date'] = self.error_class(['Please Enter Valid Date']) 
        else:
            self._errors['start_date'] = self.error_class(['Please enter date in yyyy-mm-dd format']) 
               
        if end_date:
            pass
            # ~ if end_date < timezones().date(): 
                # ~ self._errors['end_date'] = self.error_class(['Please Enter Valid Date']) 
        else:
            self._errors['end_date'] = self.error_class(['Please enter date in yyyy-mm-dd format']) 
               
        if result_date:
            pass
            # ~ if result_date < timezones().date(): 
                # ~ self._errors['result_date'] = self.error_class(['Please Enter Valid Date']) 
        else:
            self._errors['result_date'] = self.error_class(['Please enter date in yyyy-mm-dd format']) 
                
        return self.cleaned_data 


class QuizQuestionCreationForm(forms.Form):
     
    use_required_attribute = False
    requested_asset = None
    
    quiz = forms.CharField(label='Quiz', error_messages={'required' : 'The quiz field is required.'}, validators=[lambda value: check_numeric(value, 10, 'quiz')])
    
    isimage = forms.CharField(widget=forms.HiddenInput, required=False)
    question = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Please enter the  description'}), label='Question', max_length=100, min_length=2, error_messages={'required' : 'The question field is required.'})
    
    optionA = forms.CharField(label='OptionA', required=False, max_length=100, min_length=2, validators=[lambda value: alpha_space(value, 10, 'optionA')])
    optionAFile = forms.FileField(label='OptionA', widget=FileInput, required=False, validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])])
    optionB = forms.CharField(label='OptionB', required=False, max_length=100, min_length=2, validators=[lambda value: alpha_space(value, 10, 'optionB')])
    optionBFile = forms.FileField(label='OptionB', widget=FileInput, required=False, validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])])
    optionC = forms.CharField(label='OptionC', required=False, max_length=100, min_length=2, validators=[lambda value: alpha_space(value, 10, 'optionC')])
    optionCFile = forms.FileField(label='OptionC', widget=FileInput, required=False, validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])])
    optionD = forms.CharField(label='OptionD', required=False, max_length=100, min_length=2, validators=[lambda value: alpha_space(value, 10, 'optionD')])
    optionDFile = forms.FileField(label='OptionD', widget=FileInput, required=False, validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])])
    answer = forms.ChoiceField(choices=((('', '-- Select --'),('A', 'OptionA'),('B', 'OptionB'),('C', 'OptionC'),('D', 'OptionD'),)))
    status = forms.ChoiceField(choices=CHOICES)
    
    class Meta:
        model  = QuizQuestions
        fields = () 
    
    def __init__(self, *args, **kwargs):
        if 'quiz_question_id' in kwargs:
            self.quiz_question_id = kwargs.pop("quiz_question_id")
        else:
            self.quiz_question_id = 0
            
        super(QuizQuestionCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['quiz'].widget.attrs.update({'class': 'form-control'})
        self.fields['quiz'].widget.attrs.update({'class': 'form-control', 'placeholder':'Select Quiz'})
        
    def clean(self):
        cleaned_data  = super(QuizQuestionCreationForm, self).clean()
        
        
        quiz_question_id = self.quiz_question_id
        
        quiz_id = cleaned_data.get('quiz')
        if quiz_id:
            quiz_id = decrypt(quiz_id)
        isImage = cleaned_data.get("isimage", '')
        optionA = cleaned_data.get("optionA", '')
        optionB = cleaned_data.get("optionB", '')
        optionC = cleaned_data.get("optionC", '')
        optionD = cleaned_data.get("optionD", '')
        optionAFile = cleaned_data.get("optionAFile", '')
        optionBFile = cleaned_data.get("optionBFile", '')
        optionCFile = cleaned_data.get("optionCFile", '')
        optionDFile = cleaned_data.get("optionDFile", '')
        question = cleaned_data.get("question", '')
        
        
        if quiz_question_id:
            current_obj = QuizQuestions.objects.exclude(id=quiz_question_id).filter(Q(quiz_id=quiz_id, is_deleted=0), Q(question__icontains=question)).exists()
            if current_obj:
                self.add_error('question', 'Question already exist, please try another.')
                
        else:
            if question:
                current_obj = QuizQuestions.objects.filter(Q(quiz_id=quiz_id, is_deleted=0), Q(question__icontains=question)).exists()
                if current_obj:
                    self.add_error('question', 'Question already exist, please try another.')
        if isImage == 'True':
            
            if not optionAFile and not quiz_question_id:
                self.add_error('optionAFile', 'This field is required.')
            elif optionAFile:
                optionA_size = optionAFile.size
                if optionA_size > 20971520:
                    self.add_error('optionAFile', 'The file size should be less then 20MB.')
            
            if not optionBFile and not quiz_question_id:
                self.add_error('optionBFile', 'This field is required.')
            elif optionBFile:
                optionB_size = optionBFile.size
                if optionB_size > 20971520:
                    self.add_error('optionBFile', 'The file size should be less then 20MB.')
            
            if not optionCFile and not quiz_question_id:
                self.add_error('optionCFile', 'This field is required.')
            elif optionCFile:
                optionC_size = optionCFile.size
                if optionC_size > 20971520:
                    self.add_error('optionCFile', 'The file size should be less then 20MB.')
            
            if not optionDFile and not quiz_question_id:
                self.add_error('optionDFile', 'This field is required.')
            elif optionDFile:
                optionD_size = optionDFile.size
                if optionD_size > 20971520:
                    self.add_error('optionDFile', 'The file size should be less then 20MB.')
        else:
            if not optionA:
                self.add_error('optionA', 'This field in required.')
            if not optionB:
                self.add_error('optionB', 'This field in required.')
            if not optionC:
                self.add_error('optionC', 'This field in required.')
            if not optionD:
                self.add_error('optionD', 'This field in required.')
            
        return self.cleaned_data    


class QuizResultAdminCreationForm(forms.ModelForm):
     
    use_required_attribute = False
    requested_asset        = None
    
    result      = forms.IntegerField(label = 'Result', required = False)
    user        = forms.ModelChoiceField(queryset=JobUsers.objects.filter(status = True,is_active=True))
    quiz        = forms.ModelChoiceField(queryset=Quizes.objects.filter(status = True))
    timetaken   = forms.FloatField(label='Time taken',required=False)

    
    class Meta:
        model  = QuizResult
        fields = ('result','quiz','user','timetaken','question_result') 
    
    def __init__(self, *args, **kwargs):
        if 'group_id' in kwargs:
            self.group_id = kwargs.pop("group_id")
        else:
            self.group_id = 0
        super(QuizResultAdminCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['user'].widget.attrs.update({'class': 'form-control','placeholder':'Select User'})
        self.fields['result'].widget.attrs.update({'class': 'form-control','placeholder':'Enter like count','min' : 0,'value':0})
        self.fields['quiz'].widget.attrs.update({'class': 'form-control','placeholder':'Select Quiz'})
        self.fields['timetaken'].widget.attrs.update({'class': 'form-control','placeholder':'Enter time taken','min' : 0,'value':0})
        
