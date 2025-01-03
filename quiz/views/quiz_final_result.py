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
from quiz.models import QuizFinalResult
from postcategory.models import PostCategory
from americana.files import file_upload
import json, os

class QuizFinalResultAjaxView(ListView):
    model = QuizFinalResult
    permission_required = "post.view_posts"
    template_name = 'quiz/quiz_final_result/ajax_listing.html'
    paginate_by = 10
    
    def get(self, request, *args, **kwargs):
        
        dict_session = session_dict(self.request)
        
        page = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')
        
        mod_obj = QuizFinalResult.objects.filter(Q(is_deleted=False)).values('id', 'job_user__employee_name', 'job_user__employee_code','quiz__name','quiz__id','correct_questions','attempted_questions','totaltimetaken').order_by('-id')
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

class QuizFinalResultListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "post.view_posts"
    template_name       = 'quiz/quiz_final_result/listing.html'
    model               = QuizFinalResult