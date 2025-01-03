from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.template.loader import render_to_string, get_template

from .forms import *
from americana.utils import session_dict, get_client_ip, model_to_dict, timezones
from americana.encryption import encrypt, decrypt
from post.models import Posts
from postcategory.models import PostCategory

import json

class PollDeleteView(LoginRequiredMixin, DeleteView):
    model               = Posts
    template_name       = 'polls/listing.html'
    permission_required = 'post.delete_posts'
    
    def get(self, request, *args, **kwargs):
        
        context = dict()
        if request.is_ajax():
            try:
                html_form = render_to_string(
                    'base/confirm_delete.html', context, request)
            except Exception:
                html_form = render_to_string(
                    'post/listing.html', context, request)
            return JsonResponse({'html': html_form})
        else:
            return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        dict_session = session_dict(self.request)
        updated_by = dict_session['_auth_user_id']
        try :
            id = request.POST.getlist('ids[]')
            indexes = [i for i in id]
            context = dict()
            data = dict()
            for i in indexes:
                Posts.objects.filter(Q(is_deleted=False,id=decrypt(i))).update(is_deleted=True, updated_by=updated_by)
                   
            return JsonResponse({"success": True, 'msg': 'Poll has been successfully deleted.'}, status=200)
            
        except Exception:
            return JsonResponse({"success": False, 'msg': 'Some error has been occurred, please try again.'}, status=200)

class PollCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    
    permission_required = "post.add_posts"
    form_class          = PollsAdminCreationForm
    model               = Posts
    template_name       = 'polls/add.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST)
        return render(self.request, self.template_name, {"form": form})
    
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            dict_session = session_dict(self.request)
            created_by = dict_session['_auth_user_id']
            brand_id = dict_session['auth_brand_id']
            form = self.form_class(self.request.POST,request.FILES)
            
            loop_range = range(0,8)
            a_list = [] 
            for i in loop_range:
                
                emptyDict = {}
                n = str(i)
                op_str = str('label['+n+']')
                label = self.request.POST.get(op_str)
                
                if label:
                    
                    emptyDict['label'] = str(label)
                    a_list. append(emptyDict)
                    
            jsonStr = json.dumps(a_list)

            question        = self.request.POST.get('title')
            description     = self.request.POST.get('description')
            reactions       =  json.dumps(a_list)
            post_type       = 'poll'
            
            if form.is_valid():
                post = Posts(title=question, description=description, reactions=reactions, post_type=post_type, created_by=created_by, createdAt=timezones(), brand_id=brand_id, ip_address=get_client_ip(self.request))
                post.save()
                if post.id:
                    return JsonResponse({"success" : True, 'redirect_url' : reverse('polls:poll'), 'msg' : 'Poll has been created successfully.'}, status=200)
                else:
                    return JsonResponse({"success" : False, 'msg' : 'Some error has been occurred.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success":False}, status=400)


class PollUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):    
    
    permission_required = "post.change_posts"  
    model               = Posts
    form_class          = PollsAdminCreationForm
    template_name       = 'polls/edit.html'
    initial             = {'key' : 'value'}
    
    def get(self, request, *args, **kwargs):
        encrypt_pk = self.kwargs['token']
        decrypt_pk = decrypt(encrypt_pk) 
        
        groups  = get_object_or_404(Posts, pk=decrypt_pk, is_deleted=False)
        
        dictionary = model_to_dict(Posts.objects.filter(pk=decrypt_pk, is_deleted=False).only('title', 'description', 'status','reactions')[0])
        form = self.form_class(initial=dictionary)
        
        if dictionary['reactions']:
            reaction = json.loads(dictionary['reactions'])
        else:
            reaction = ''
        return render(self.request, self.template_name, {"form": form, 'id' : encrypt_pk , 'reactions' :  reaction, 'vi' :'0'})
        
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            
            encrypt_pk   = self.kwargs['token']
            decrypt_pk   = decrypt(encrypt_pk) 
            dict_session = session_dict(self.request)
            updated_by   = dict_session['_auth_user_id']
            form         = self.form_class(self.request.POST, request.FILES)
            loop_range = range(0,8)
            a_list = [] 
            for i in loop_range:
                emptyDict = {}
                n = str(i)
                op_str = str('label['+n+']')
                label = self.request.POST.get(op_str)
                
                if label:
                    emptyDict['label'] = str(label)
                    a_list. append(emptyDict)
                    
            jsonStr = json.dumps(a_list)
            question    = self.request.POST.get('title')
            description = self.request.POST.get('description')
            reactions   =  json.dumps(a_list)
            post_type   = 'poll'
            status      = True
            
            if form.is_valid():
                try:
                    Posts.objects.filter(id=decrypt_pk).update(title=question, description=description, reactions=reactions, updated_by=updated_by, updatedAt=timezones(), ip_address=get_client_ip(self.request))
                    return JsonResponse({"success" : True, 'redirect_url' : reverse('polls:poll'), 'msg' : 'Poll has been updated successfully.'}, status=200)
                except:
                    return JsonResponse({"success" : False, 'msg' : 'Some error has been occurred.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success" : False}, status=400)
    
    
    
class PollListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "post.view_posts"
    template_name       = 'polls/listing.html'
    model               = Posts


class PollAjaxView(ListView):
    model               =  Posts
    permission_required = "post.view_posts"
    template_name       = 'polls/ajax_listing.html'
    paginate_by         = 10
    
    def get(self, request, *args, **kwargs):
        
        dict_session = session_dict(self.request)
        auth_brand_id = dict_session['auth_brand_id']
        page = request.GET.get('page', 1)
        
        filter_val = request.GET.get('keywords', '')
        print('brnad', auth_brand_id)
        if auth_brand_id:
            brand_filter = Q(is_deleted=False, post_type='poll', brand_id=auth_brand_id)
        else:
            brand_filter = Q(is_deleted=False, post_type='poll')
        
        mod_obj = Posts.objects.filter((Q(title__icontains=filter_val) | Q(description__icontains=filter_val) | Q(post_type__icontains=filter_val) | Q(post_category__name__icontains=filter_val) | Q(user__employee_code__icontains=filter_val)), brand_filter).values('id', 'title', 'description', 'post_type', 'user__employee_code', 'post_category__name', 'approve_status', 'status', 'reactions', 'createdAt').order_by('-id')
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

