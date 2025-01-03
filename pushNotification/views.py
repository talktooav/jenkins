from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, FormView, UpdateView, ListView, DeleteView
from django.shortcuts import render,redirect, get_object_or_404
from .ajax_views import *
from django.http import JsonResponse
from django.db.models import Q, Count
from americana.utils import model_to_dict, timezones
from .forms import *
from django.conf import settings   
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from americana.utils import session_dict, get_client_ip, send_push_notification
from americana.encryption import encrypt, decrypt
from jobusers.models import JobUsers
from .models import *
import requests
import json

# ~ from devices.models import Devices
class PushDeleteView(LoginRequiredMixin, DeleteView):
    model               = PushNotification
    template_name       = 'pushnotification/listing.html'
    # ~ permission_required = 'enterprise_groups.delete_enterprise_groups'
    
    def get(self, request, *args, **kwargs):
        
        context = dict()
        if request.is_ajax():
            data              = dict()
            html              = render_to_string('pushnotification/deleteApp.html', context, request)
            data['html_form'] = True    
            
            return JsonResponse({'html_form': data, 'html': html})
        else:
            return render(request, 'pushnotification/listing.html')

    def post(self, request, *args, **kwargs):
        dict_session = session_dict(self.request)
        # ~ auth_slug    = dict_session['auth_user_slug']
        try :
            id      = request.POST.getlist('ids[]')
            # ~ indexes = [int(decrypt(i)) for i in id]
            indexes = [int((i)) for i in id]
            groupObj = [i.id for i in push_notification.objects.filter(Q(is_deleted=False))]
            context = dict()
            data = dict()
            for i in indexes:
                
                        push_notification.objects.filter(Q(is_deleted=False,id=i)).update(is_deleted=True)
                   
            html = render_to_string('pushnotification/deleteApp.html', {'context':context}, request)
            if context:
                data['html'] = html
                data['response'] = False
                return JsonResponse(data)
                    
            else:
                url_link    = reverse_lazy('post:{}'.format('post'))
                data['url'] = url_link
                data['response'] = True
                data['success'] = True
                data['msg'] = 'Record Deleted Successfully'
                return JsonResponse(data, status = 200)
            
        except template.TemplateDoesNotExist:
            return render(request, 'pushnotification/listing.html')

class PushCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    
    permission_required = "account.add_push_notification"
    form_class          = PushAdminCreationForm
    model               = PushNotification
    template_name       = 'pushnotification/add.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST)
        return render(self.request, self.template_name, {"form": form})
    
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            dict_session  = session_dict(self.request)
            created_by    = dict_session['_auth_user_id']
            form    = self.form_class(self.request.POST)
            context = {
                'form' : form
            }
            title                = self.request.POST.get('title')
            description          = self.request.POST.get('description')
            user_id              = self.request.POST.get('user')
            job_role             = self.request.POST.get('job_role')
            link                 = self.request.POST.get('link')
            schedule_date_time   = self.request.POST.get('schedule_date_time')
            schedule_date_time   = schedule_date_time if schedule_date_time else '2'
            sent_status          = 0
            
            if form.is_valid():
                if user_id:
                    user_data = CustomUser.objects.filter(id = user_id).values('id', 'device_id','phone','first_name','middle_name','last_name','email','date_of_birth')
                    if user_data.exists():
                        sent_status = 1
                        payload = {"to":user_data[0]['device_id'], "notification" : {"body" : description,"title" : title,"content_available" : "true","priority" : "high"},"data" : {"body" : description,"title" : title,"content_available" : "true","priority" : "high"}}
                        response = send_push_notification(payload)
                if job_role:
                    job_role_data = CustomUser.objects.filter(job_role_id  = job_role).values('id', 'device_id','phone','first_name','middle_name','last_name','email','date_of_birth')
                    if job_role_data.exists():
                        for user in job_role_data:
                            # ~ post_ids.append(item['post_id'])
                            sent_status = 1
                            payload = {"to":user['device_id'], "notification" : {"body" : description,"title" : title,"content_available" : "true","priority" : "high"},"data" : {"body" : description,"title" : title,"content_available" : "true","priority" : "high"}}
                            response = send_push_notification(payload)
               
                pushnotification = push_notification(title=title,description=description,user_id=user_id,job_role_id =job_role,link=link,schedule_date_time=schedule_date_time, createdAt=timezones(),sent_status=sent_status)
                pushnotification.save()
                return JsonResponse({"success" : True, 'redirect_url' : reverse('pushnotification:pushnotification'), 'msg' : 'Data has been created successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success":False}, status=400)


class PushUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):    
    
    permission_required = "account.change_moderation"  
    model               = PushNotification
    form_class          = PushAdminCreationForm
    template_name       = 'pushnotification/edit.html'
    initial             = {'key' : 'value'}
    
    def get(self, request, *args, **kwargs):
        encrypt_pk = self.kwargs['token']
        decrypt_pk = (encrypt_pk) 
        # ~ decrypt_pk = decrypt(encrypt_pk) 
       
        context    = {}
        push     = get_object_or_404(push_notification, pk=decrypt_pk, is_deleted=False)
        dictionary = model_to_dict(push_notification.objects.filter(pk=decrypt_pk, is_deleted=False).only('title', 'description')[0])
        
        form = self.form_class(initial=dictionary)
       
        return render(self.request, self.template_name, {"form": form, 'id' : encrypt_pk})
        
    def post(self, request, *args, **kwargs):
        if self.request.method == "POST" and self.request.is_ajax():
            encrypt_pk   = self.kwargs['token']
            decrypt_pk   = (encrypt_pk) 
            dict_session = session_dict(self.request)
            updated_by   = dict_session['_auth_user_id']
            auth_slug    = dict_session['auth_user_slug']
            
            form          = self.form_class(self.request.POST, id=decrypt_pk)
            title          = request.POST.get('title')
            description   = request.POST.get('description')
            post_type        = self.request.POST.get('post_type')
            user_id          = self.request.POST.get('user_id')
            post_category    = self.request.POST.get('post_category')
            post_image       = self.request.POST.get('post_image')
            post_file        = self.request.POST.get('post_file')
            file_type        = self.request.POST.get('file_type')
            taggedusers      = self.request.POST.get('taggedusers')
            like_count       = self.request.POST.get('like_count')
            comment_count    = self.request.POST.get('comment_count')
            approve_status   = self.request.POST.get('approve_status')
            status           = self.request.POST.get('status')
            
            if form.is_valid():
               posts = push_notification.objects.get(id=decrypt_pk, is_deleted=False)
               
               posts.title        = title
               posts.description = description
               posts.post_type = post_type
               posts.user_id_id = user_id
               posts.post_category_id = post_category
               posts.post_image = post_image
               posts.post_file = post_file
               posts.file_type = file_type
               posts.taggedusers = taggedusers
               posts.like_count = like_count
               posts.comment_count = comment_count
               posts.approve_status = approve_status
               posts.status = status
               posts.updated_by  = updated_by
               posts.ip_address  = get_client_ip(self.request)
               posts.updatedAt   = timezones()
              
               posts.save()
               return JsonResponse({"success" : True, 'redirect_url' : reverse('pushnotification:pushnotification'), 'msg' : 'Data has been updated successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success" : False}, status=400)
    
    
    
class PushListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "account.view_posts"
    template_name = 'pushnotification/listing.html'
    model = PushNotification


class PushAjaxView(ListView):
    model               =  PushNotification
    permission_required = "account.view_push_notification"
    template_name       = 'pushnotification/ajax_listing.html'
    paginate_by         = 10
    
    def get(self, request, *args, **kwargs):
        
        dict_session       = session_dict(self.request)
        # ~ auth_enterprise_id = dict_session['auth_enterprise_id']
        
        page       = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')
        
        mod_obj = push_notification.objects.filter((Q(title__icontains=filter_val) | Q(description__icontains=filter_val) | Q(user_id__email__icontains=filter_val) | Q(job_role_id__name__icontains=filter_val) | Q(link__icontains=filter_val)),
            Q(is_deleted__icontains=False)).values('id', 'title', 'description','sent_status','link','schedule_date_time','job_role_id__name','user_id__email').order_by('-id')
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
