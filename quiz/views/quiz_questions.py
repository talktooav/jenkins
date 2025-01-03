from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Count
from django.conf import settings
from django.core.paginator import Paginator
from django.template.loader import render_to_string, get_template

from quiz.forms import *
from americana.utils import session_dict, get_client_ip, model_to_dict, timezones
from americana.encryption import encrypt, decrypt
from quiz.models import QuizQuestions
from postcategory.models import PostCategory
from americana.files import file_upload
import json, os

QUESTION_FILE_LOCATION = '/root/americana/Americana/americana/static_cdn/upload_media/quiz/questions/'
QUESTION_UPLOAD_PATH = '/media/quiz/questions/'


class QuizQuestionDeleteView(LoginRequiredMixin, DeleteView):
    model = QuizQuestions
    template_name = 'quiz/quiz_questions/listing.html'
    permission_required = "quiz.delete_quizquestions"
    
    def get(self, request, *args, **kwargs):
        context = dict()
        if request.is_ajax():
            try:
                html_form = render_to_string(
                    'base/confirm_delete.html', context, request)
            except Exception:
                html_form = render_to_string(
                    'quiz/quiz_questions/listing.html', context, request)
            return JsonResponse({'html': html_form})
        else:
            return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        dict_session = session_dict(self.request)
        updated_by = dict_session['_auth_user_id']
        
        if self.request.is_ajax():
            # ~ try:
            idd = self.request.POST.getlist('ids[]')
            indexes = [int(decrypt(i)) for i in idd]
            # ~ print('idne', indexes)
            obj = QuizQuestions.objects.filter(
                Q(is_deleted=False),
                Q(id__in=indexes))

            if obj:
                obj.update(is_deleted=True)
                return JsonResponse({
                    "success": True,
                    'msg': 'Question has been successfully deleted.'},
                     status=200)
                
            # ~ except Exception:
                # ~ return JsonResponse({
                    # ~ "success": False,
                    # ~ 'msg': 'Some error has been occurred, please try again.'},
                     # ~ status=200)
        else:
            return self.delete(*args, **kwargs)


class QuizQuestionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    
    permission_required = "quiz.add_quizquestions"
    form_class = QuizQuestionCreationForm
    model = QuizQuestions
    template_name = 'quiz/quiz_questions/add.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST)
        dict_session = session_dict(self.request)
        created_by = dict_session['_auth_user_id']
        auth_brand_id = int(dict_session['auth_brand_id'])
        
        if auth_brand_id:
            brand_filter = Q(brand_id=auth_brand_id, is_deleted=False)
        else:
            brand_filter = Q(is_deleted=False)
        quizs = Quizes.objects.filter(brand_filter).values_list('id', 'name').order_by('name')
        return render(self.request, self.template_name, {"form": form, 'quizs' : quizs})
    
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            dict_session = session_dict(self.request)
            created_by = dict_session['_auth_user_id']
            
            dict_session = session_dict(self.request)
            created_by = dict_session['_auth_user_id']
            auth_brand_id = dict_session['auth_brand_id']
            ip_address = get_client_ip(self.request)
            form = self.form_class(request.POST,request.FILES)
            
            quiz_id = decrypt(request.POST.get('quiz'))
            question = request.POST.get('question')
            quiz = request.POST.get('quiz')
            isImage = request.POST.get('isimage')
            
            optionJson = dict()
            optionA = ''
            optionB = ''
            optionC = ''
            optionD = ''
            if isImage == 'True':
                optionAFile = request.FILES['optionAFile']
                upload_optionA = file_upload(optionAFile, QUESTION_FILE_LOCATION, QUESTION_UPLOAD_PATH)    
                if upload_optionA==False:
                    return JsonResponse({"success" : False, 'msg' : 'Some error has been occurred with optionA, please try again.'}, status=200)
                else:
                    optionA = settings.BASE_URL+upload_optionA['upload_url']
                
                optionBFile = request.FILES['optionBFile']
                upload_optionB = file_upload(optionBFile, QUESTION_FILE_LOCATION, QUESTION_UPLOAD_PATH)    
                if upload_optionB==False:
                    return JsonResponse({"success" : False, 'msg' : 'Some error has been occurred with optionB, please try again.'}, status=200)
                else:
                    optionB = settings.BASE_URL+upload_optionB['upload_url']
                
                optionCFile = request.FILES['optionCFile']
                upload_optionC = file_upload(optionCFile, QUESTION_FILE_LOCATION, QUESTION_UPLOAD_PATH)    
                if upload_optionC==False:
                    return JsonResponse({"success" : False, 'msg' : 'Some error has been occurred with optionC, please try again.'}, status=200)
                else:
                    optionC = settings.BASE_URL+upload_optionC['upload_url']
                
                optionDFile = request.FILES['optionDFile']
                upload_optionD = file_upload(optionDFile, QUESTION_FILE_LOCATION, QUESTION_UPLOAD_PATH)    
                if upload_optionD==False:
                    return JsonResponse({"success" : False, 'msg' : 'Some error has been occurred with optionD, please try again.'}, status=200)
                else:
                    optionD = settings.BASE_URL+upload_optionD['upload_url']
            else:
                optionA = request.POST.get('optionA')
                optionB = request.POST.get('optionB')
                optionC = request.POST.get('optionC')
                optionD = request.POST.get('optionD')
            
            answer = request.POST.get('answer')

            optionJson['optionA'] = optionA
            optionJson['optionB'] = optionB
            optionJson['optionC'] = optionC
            optionJson['optionD'] = optionD
            optionJson['answer'] = answer
            
            
            if form.is_valid():
                quiz_question = QuizQuestions(
                        quiz_id = quiz_id,
                        question = question,
                        isimage = isImage,
                        options = optionJson,
                        ip_address = ip_address,
                        created_by = created_by,
                        brand_id = auth_brand_id,
                        createdAt = timezones()
                )
                quiz_question.save()
                
                return JsonResponse({"success" : True, 'redirect_url' : reverse('quiz:quiz-question-listing'), 'msg' : 'Question has been added successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success":False}, status=400)


class QuizQuestionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):    
    
    permission_required = "quiz.change_quizquestions"
    model = QuizQuestions
    form_class = QuizQuestionCreationForm
    template_name = 'quiz/quiz_questions/edit.html'
    initial = {'key' : 'value'}
    
    def get(self, request, *args, **kwargs):
        encrypt_pk = self.kwargs['token']
        decrypt_pk = decrypt(encrypt_pk) 
        dict_session = session_dict(self.request)
        created_by = dict_session['_auth_user_id']
        auth_brand_id = int(dict_session['auth_brand_id'])
        
        if auth_brand_id:
            brand_filter = Q(brand_id=auth_brand_id, is_deleted=False)
        else:
            brand_filter = Q(is_deleted=False)
        
        quizs = Quizes.objects.filter(brand_filter).values_list('id', 'name').order_by('name')

        dictionary = model_to_dict(QuizQuestions.objects.filter(pk=decrypt_pk, is_deleted=False).only('id', 'question', 'options', 'isimage', 'status')[0])
        value_obj = dictionary
        value_obj['optionA'] = dictionary['options']['optionA']
        value_obj['optionB'] = dictionary['options']['optionB']
        value_obj['optionC'] = dictionary['options']['optionC']
        value_obj['optionD'] = dictionary['options']['optionD']
        value_obj['answer'] = dictionary['options']['answer']
        form = self.form_class(initial=dictionary)

        return render(self.request, self.template_name, {"form": form, 'id' : encrypt_pk, 'quizs' : quizs})
        
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            
            encrypt_pk = self.kwargs['token']
            decrypt_pk = decrypt(encrypt_pk) 
            dict_session = session_dict(self.request)
            
            updated_by = dict_session['_auth_user_id']
            ip_address = get_client_ip(self.request)
            form = self.form_class(self.request.POST, request.FILES, quiz_question_id=decrypt_pk)
            
            quiz_question_obj = QuizQuestions.objects.filter(pk=decrypt_pk, is_deleted=False).only('id', 'question', 'options', 'isimage', 'status')
            
            quiz_id = decrypt(request.POST.get('quiz'))
            question = request.POST.get('question')
            quiz = request.POST.get('quiz')
            isImage = request.POST.get('isimage')
            
            optionJson = quiz_question_obj[0].options
            optionA = ''
            optionB = ''
            optionC = ''
            optionD = ''
            if isImage == 'True':
                if 'optionAFile' in request.FILES:
                    optionAFile = request.FILES['optionAFile']
                    upload_optionA = file_upload(optionAFile, QUESTION_FILE_LOCATION, QUESTION_UPLOAD_PATH)    
                    if upload_optionA==False:
                        return JsonResponse({"success" : False, 'msg' : 'Some error has been occurred with optionA, please try again.'}, status=200)
                    else:
                        existoptionA = optionJson['optionA'].replace(settings.BASE_URL+'/media/quiz/questions', '')
                        if os.path.exists(QUESTION_FILE_LOCATION+'/'+existoptionA):
                            os.remove(QUESTION_FILE_LOCATION+'/'+existoptionA)
                        optionA = settings.BASE_URL+upload_optionA['upload_url']
                
                if 'optionBFile' in request.FILES:
                    optionBFile = request.FILES['optionBFile']
                    upload_optionB = file_upload(optionBFile, QUESTION_FILE_LOCATION, QUESTION_UPLOAD_PATH)    
                    if upload_optionB==False:
                        return JsonResponse({"success" : False, 'msg' : 'Some error has been occurred with optionB, please try again.'}, status=200)
                    else:
                        existoptionB = optionJson['optionB'].replace(settings.BASE_URL+'/media/quiz/questions', '')
                        if os.path.exists(QUESTION_FILE_LOCATION+'/'+existoptionB):
                            os.remove(QUESTION_FILE_LOCATION+'/'+existoptionB)
                        optionB = settings.BASE_URL+upload_optionB['upload_url']
                
                if 'optionCFile' in request.FILES:                
                    optionCFile = request.FILES['optionCFile']
                    upload_optionC = file_upload(optionCFile, QUESTION_FILE_LOCATION, QUESTION_UPLOAD_PATH)    
                    if upload_optionC==False:
                        return JsonResponse({"success" : False, 'msg' : 'Some error has been occurred with optionC, please try again.'}, status=200)
                    else:
                        existoptionC = optionJson['optionC'].replace(settings.BASE_URL+'/media/quiz/questions', '')
                        if os.path.exists(QUESTION_FILE_LOCATION+'/'+existoptionC):
                            os.remove(QUESTION_FILE_LOCATION+'/'+existoptionC)
                        optionC = settings.BASE_URL+upload_optionC['upload_url']
                if 'optionDFile' in request.FILES:
                    optionDFile = request.FILES['optionDFile']
                    upload_optionD = file_upload(optionDFile, QUESTION_FILE_LOCATION, QUESTION_UPLOAD_PATH)    
                    if upload_optionD==False:
                        return JsonResponse({"success" : False, 'msg' : 'Some error has been occurred with optionD, please try again.'}, status=200)
                    else:
                        existoptionD = optionJson['optionD'].replace(settings.BASE_URL+'/media/quiz/questions', '')
                        if os.path.exists(QUESTION_FILE_LOCATION+'/'+existoptionD):
                            os.remove(QUESTION_FILE_LOCATION+'/'+existoptionD)
                        optionD = settings.BASE_URL+upload_optionD['upload_url']
            else:
                optionA = request.POST.get('optionA')
                optionB = request.POST.get('optionB')
                optionC = request.POST.get('optionC')
                optionD = request.POST.get('optionD')
            
            answer = request.POST.get('answer')
            if optionA:
                optionJson['optionA'] = optionA
            if optionB:
                optionJson['optionB'] = optionB
            if optionC:
                optionJson['optionC'] = optionC
            if optionD:
                optionJson['optionD'] = optionD
            if answer:
                optionJson['answer'] = answer
            
            
            if form.is_valid():
                quiz_question_obj.update(
                        quiz_id = quiz_id,
                        question = question,
                        isimage = isImage,
                        options = optionJson,
                        ip_address = ip_address,
                        updated_by = updated_by,
                        updatedAt = timezones()
                )
                return JsonResponse({"success" : True, 'redirect_url' : reverse('quiz:quiz-question-listing'), 'msg' : 'Question has been updated successfully.'}, status=200)
            else:
                return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success" : False}, status=400)
    
    
    
class QuizQuestionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "quiz.view_quizquestions"
    template_name = 'quiz/quiz_questions/listing.html'
    model = QuizQuestions


class QuizQuestionAjaxView(ListView):
    model = QuizQuestions
    permission_required = "quiz.view_quizquestions"
    template_name = 'quiz/quiz_questions/ajax_listing.html'
    paginate_by = 10
    
    def get(self, request, *args, **kwargs):
        
        dict_session = session_dict(self.request)
        auth_brand_id = int(dict_session['auth_brand_id'])
        
        page = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')
        if auth_brand_id:
            brand_filter = Q(is_deleted=False, brand_id=auth_brand_id)
        else:
            brand_filter = Q(is_deleted=False)
        
        mod_obj = QuizQuestions.objects.filter(brand_filter).values('id', 'quiz__name', 'question', 'options', 'status', 'createdAt').order_by('-id')
        total_count = mod_obj.count()
       
        if total_count == 0:
            total_count = 'No'
        paginator   = Paginator(mod_obj, self.paginate_by)
        try:
            devices = paginator.page(page)
        except PageNotAnInteger:
            devices = paginator.page(1)
        except EmptyPage:
            devices = paginator.page(paginator.num_pages)
            
        if request.is_ajax():
            context                = dict()
            context['object_list'] = devices
            context['pagination']  = 'base/pagination.html'
            
            html_form = render_to_string(
                self.template_name, {'context' : context}, request)
            html_pagi = render_to_string(
                'base/pagination.html', {'context' : context}, request)
            return JsonResponse({'html': html_form, 'pagination' : html_pagi, 'total_records' : str(total_count)+' records found'})
        else:
            return super().get(request, *args, **kwargs)
        return JsonResponse(data)

