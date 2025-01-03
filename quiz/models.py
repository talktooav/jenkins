from django.db import models
from americana.utils import cust_timezone
from django.contrib.postgres.fields import ArrayField
from jobusers.models import JobUsers
from postcategory.models import PostCategory
from americana.constants import APPROVE_STATUS_CHOICES, POST_LANGUAGE


class Quizes(models.Model):
    name = models.TextField(blank = True, null= True)
    description = models.TextField(blank = True,null=True)
    start_date = models.DateField(auto_now_add=False, blank=True, null=True)
    end_date = models.DateField(auto_now_add=False, blank=True, null=True)
    result_date = models.DateField(auto_now_add=False, blank=True, null=True)
    createdAt = models.DateTimeField(default=cust_timezone())
    updatedAt = models.DateTimeField(auto_now_add=True, null=True)
    approve_status = models.IntegerField(choices=APPROVE_STATUS_CHOICES, default=0 )
    isimage = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.IntegerField(default=0)
    updated_by = models.IntegerField(default=0)
    brand_id = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        db_table = 'amrc_quiz'
        
    def __str__(self):
        return str(self.name)


class QuizQuestions(models.Model):
    
    quiz = models.ForeignKey(Quizes, on_delete=models.PROTECT, null=True)
    question = models.JSONField(blank=True, null=True)
    isimage = models.BooleanField(default=False)
    options = models.JSONField(blank=True, null=True)
    createdAt = models.DateTimeField(default=cust_timezone())
    updatedAt =	models.DateTimeField(auto_now_add=True, null=True)
    status = models.BooleanField(default = True)
    is_deleted = models.BooleanField(default = False)
    created_by = models.IntegerField(default=0)
    updated_by = models.IntegerField(default=0)
    brand_id = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        db_table = 'amrc_quiz_questions'
        
    def __str__(self):
        return str(self.question)


class QuizResult(models.Model):
    quiz = models.ForeignKey(Quizes, on_delete=models.PROTECT, null=True)
    quiz_question = models.ForeignKey(QuizQuestions, on_delete=models.PROTECT, null=True)
    question_result = models.BooleanField(default=False)
    quiz_completed = models.BooleanField(default=False)
    job_user = models.ForeignKey(JobUsers, on_delete=models.PROTECT, null=True)

    timetaken = models.FloatField(default=0.0)
    createdAt = models.DateTimeField(default=cust_timezone())
    answer_given = models.CharField(blank = True, null= True,max_length=30)
    correct_answer = models.CharField(blank = True, null= True,max_length=30)
    updatedAt = models.DateTimeField(auto_now_add=True, null=True)
    is_deleted = models.BooleanField(default = False)

    class Meta:
        db_table = 'amrc_quiz_result'


class QuizFinalResult(models.Model):
    quiz = models.ForeignKey(Quizes, on_delete=models.PROTECT, null=True)
    job_user = models.ForeignKey(JobUsers, on_delete=models.PROTECT, null=True)
    total_questions = models.IntegerField(default=0)
    correct_questions = models.IntegerField(default=0)
    attempted_questions = models.IntegerField(default=0)
    totaltimetaken = models.FloatField(default=0.0)
    createdAt = models.DateTimeField(default=cust_timezone())
    updatedAt = models.DateTimeField(auto_now_add=True, null=True)
    is_deleted = models.BooleanField(default = False)
    share = models.BooleanField(default = False)
    class Meta:
        db_table = 'amrc_quiz_final_result'
    
