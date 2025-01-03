from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.template.loader import render_to_string, get_template

from quiz.forms import *
from americana.utils import session_dict, get_client_ip, model_to_dict, timezones
from americana.encryption import encrypt, decrypt
from quiz.models import Quizes
from postcategory.models import PostCategory
import json


class QuizDeleteView(LoginRequiredMixin, DeleteView):
    model               = Quizes
    template_name       = 'quiz/listing.html'
    permission_required = 'quiz.delete_quizes'
    
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
        try :
            id = request.POST.getlist('ids[]')
            indexes = [int((i)) for i in id]
            groupObj = [i.id for i in Quizes.objects.filter(Q(is_deleted=False))]
            context = dict()
            data = dict()
            for i in indexes:
                Quizes.objects.filter(Q(is_deleted=False,id=i)).update(is_deleted=True, updated_by=updated_by)
            
            return JsonResponse({"success": True, 'msg': 'Quiz has been successfully deleted.'}, status=200)
                
        except Exception:
            return JsonResponse({"success": False, 'msg': 'Some error has been occurred, please try again.'}, status=200)


class QuizCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    
    permission_required = "quiz.add_quizes"
    form_class          = QuizAdminCreationForm
    model               = Quizes
    template_name       = 'quiz/add.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST)
        return render(self.request, self.template_name, {"form": form})
    
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            dict_session  = session_dict(self.request)
            form = self.form_class(self.request.POST,request.FILES)

            created_by = dict_session['_auth_user_id']
            auth_brand_id = dict_session['auth_brand_id']
            dict_session = session_dict(self.request)
            created_by = dict_session['_auth_user_id']
            ip_address = get_client_ip(self.request)
            
            name = self.request.POST.get('name')
            start_date = self.request.POST.get('start_date')
            end_date = self.request.POST.get('end_date')
            result_date = self.request.POST.get('result_date')
            isimage = self.request.POST.get('isimage')
            approve_status = self.request.POST.get('approve_status')
            
            if form.is_valid():
                logo = False
                quiz = Quizes(
                        name = name,
                        start_date = start_date,
                        end_date = end_date,
                        result_date = result_date,
                        ip_address = ip_address,
                        created_by = created_by,
                        approve_status = approve_status,
                        isimage = isimage,
                        createdAt = timezones(),
                        brand_id = auth_brand_id
                )
                quiz.save()
                
                return JsonResponse({"success" : True, 'redirect_url' : reverse('quiz:quiz'), 'msg' : 'Quiz has been created successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success":False}, status=400)


class QuizUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):    
    
    permission_required = "quiz.change_quizes"  
    model               = Quizes
    form_class          = QuizAdminCreationForm
    template_name       = 'quiz/edit.html'
    initial             = {'key' : 'value'}
    
    def get(self, request, *args, **kwargs):
        encrypt_pk = self.kwargs['token']
        decrypt_pk = decrypt(encrypt_pk) 
        # ~ groups  = get_object_or_404(Quizes, pk=decrypt_pk, is_deleted=False)
        dictionary = model_to_dict(Quizes.objects.filter(pk=decrypt_pk, is_deleted=False).only('name', 'start_date', 'end_date','result_date')[0])
        form = self.form_class(initial=dictionary, group_id=decrypt_pk)
        return render(self.request, self.template_name, {"form": form, 'id' : encrypt_pk})
        
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            
            encrypt_pk = self.kwargs['token']
            decrypt_pk = decrypt(encrypt_pk) 
            dict_session = session_dict(self.request)
            updated_by = dict_session['_auth_user_id']
            form = self.form_class(self.request.POST, request.FILES)
            name = self.request.POST.get('name')
            start_date = self.request.POST.get('start_date')
            end_date = self.request.POST.get('end_date')
            result_date = self.request.POST.get('result_date')
            status = True
            
            if form.is_valid():
                Quizes.objects.filter(id=decrypt_pk).update(name=name, start_date=start_date,result_date=result_date,end_date=end_date, updated_by=updated_by, updatedAt=timezones(), ip_address=get_client_ip(self.request))
                return JsonResponse({"success" : True, 'redirect_url' : reverse('quiz:quiz'), 'msg' : 'Quiz has been updated successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success" : False}, status=400)
        
    
class QuizListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "quiz.view_quizes"
    template_name       = 'quiz/listing.html'
    model               = Quizes


class QuizAjaxView(ListView):
    model               =  Quizes
    permission_required = "quiz.view_quizes"
    template_name       = 'quiz/ajax_listing.html'
    paginate_by         = 10
    
    def get(self, request, *args, **kwargs):
        
        dict_session = session_dict(self.request)
        auth_brand_id = int(dict_session['auth_brand_id'])
        
        page = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')
        
        if auth_brand_id:
            brand_filter = Q(is_deleted=False, brand_id=auth_brand_id)
        else:
            brand_filter = Q(is_deleted=False)
        mod_obj = Quizes.objects.filter(brand_filter).values('id', 'name', 'start_date', 'end_date', 'result_date', 'approve_status', 'isimage', 'status', 'createdAt').order_by('-id')
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
