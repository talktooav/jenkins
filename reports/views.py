from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Count

from django.core.paginator import Paginator
from django.template.loader import render_to_string, get_template
from americana.utils import session_dict, get_client_ip, model_to_dict, timezones
from americana.encryption import encrypt, decrypt
from jobusers.models import JobUsers
from post.models import Posts, PostsReaction

import csv
import datetime
from datetime import timedelta
from django.http import HttpResponse


class DownloadInactiveEmployeesView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'account.view_customusers'
    
    def get(self, request, *args, **kwargs):
    
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="app_data_usage.csv"'
        
        
        filter_val = request.GET.get('keywords', '')
        
        
        writer = csv.writer(response)
        writer.writerow(['Employee Name', 'Employee Code', 'DOB', 'Created'])
        
        user_data = JobUsers.objects.filter((Q(employee_name__icontains=filter_val) | Q(employee_code__icontains=filter_val)), Q(status__icontains=True),Q(logged_in_time__isnull=True)).values('id', 'employee_name','employee_code','createdAt','date_of_birth').order_by('-id')

        for user in user_data:
            
            writer.writerow([user['employee_name'], user['employee_code'], user['date_of_birth'], user['createdAt']])
        return response


        
class InactiveEmployeesView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "account.view_customusers"
    template_name       = 'reports/inactive_employees.html'  
    model               = JobUsers
    
 
class InactiveEmployeesAjaxView(ListView):
    model               =  JobUsers
    template_name       = 'reports/ajax_inactive_employees.html'
    paginate_by         = 10
    
    def get(self, request, *args, **kwargs):
        
        dict_session       = session_dict(self.request)
        # ~ auth_enterprise_id = dict_session['auth_enterprise_id']
        # ~ print(request.path)
        page       = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')
        # ~ and account_postsreaction.post_track_status = True
        mod_obj = JobUsers.objects.filter((Q(employee_name__icontains=filter_val) | Q(employee_code__icontains=filter_val)), Q(status__icontains=True),Q(logged_in_time__isnull=True)).values('id', 'employee_name','employee_code','createdAt','date_of_birth').order_by('-id')
        # ~ print(mod_obj.query)
        total_count = mod_obj.count()
        # ~ print('total_count=>',total_count)
        if total_count == 0:
            total_count = 'No'
        paginator   = Paginator(mod_obj, self.paginate_by)
        try:
            report = paginator.page(page)
        except PageNotAnInteger:
            report = paginator.page(1)
        except EmptyPage:
            report = paginator.page(paginator.num_pages)
            
        if request.is_ajax():
            context                = dict()
            context['object_list'] = report
            context['pagination']  = 'base/pagination.html'
            
            html_form = render_to_string(
                self.template_name, {'context' : context}, request)
            html_pagi = render_to_string(
                'base/pagination.html', {'context' : context}, request)
            return JsonResponse({'html': html_form, 'pagination' : html_pagi, 'total_records' : str(total_count)+' records found'})
        else:
            return super().get(request, *args, **kwargs)
        return JsonResponse(data)
        
        
class DownloadInactiveUsersView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'account.view_customusers'
    
    def get(self, request, *args, **kwargs):
    
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="app_data_usage.csv"'
        
        
        filter_val = request.GET.get('keywords', '')
       
        
        writer = csv.writer(response)
        writer.writerow(['Employee Name','Employee Code', 'DOB', 'Last Logged In','Created'])
        
        time_threshold = datetime.date.today() - timedelta(days=15)
        user_data =  mod_obj = JobUsers.objects.filter((Q(employee_name__icontains=filter_val) | Q(employee_code__icontains=filter_val)), Q(logged_in_time__lt = time_threshold), Q(status__icontains=True)).values('id', 'employee_name','employee_code','createdAt','date_of_birth','logged_in_time').order_by('-id')

        for user in user_data:
            
            writer.writerow([user['employee_name'], user['employee_code'], user['date_of_birth'], user['logged_in_time'], user['createdAt']])
        return response


        
class InactiveUsersView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "account.view_customusers"
    template_name       = 'reports/inactive_users.html'  
    model               = JobUsers
    
 
class InactiveUsersAjaxView(ListView):
    model               =  JobUsers
    template_name       = 'reports/ajax_inactive_users.html'
    paginate_by         = 10
    
    def get(self, request, *args, **kwargs):
        
        dict_session       = session_dict(self.request)
        # ~ auth_enterprise_id = dict_session['auth_enterprise_id']
        # ~ print(request.path)
        page       = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')
        # ~ and account_postsreaction.post_track_status = True
        time_threshold = datetime.date.today() - timedelta(days=15)
        mod_obj = JobUsers.objects.filter((Q(employee_name__icontains=filter_val) | Q(employee_code__icontains=filter_val)), Q(logged_in_time__lt = time_threshold), Q(status__icontains=True)).values('id', 'employee_name','employee_code','createdAt','date_of_birth','logged_in_time').order_by('-id')
        
        total_count = mod_obj.count()
        # ~ print('total_count=>',total_count)
        if total_count == 0:
            total_count = 'No'
        paginator   = Paginator(mod_obj, self.paginate_by)
        try:
            report = paginator.page(page)
        except PageNotAnInteger:
            report = paginator.page(1)
        except EmptyPage:
            report = paginator.page(paginator.num_pages)
            
        if request.is_ajax():
            context                = dict()
            context['object_list'] = report
            context['pagination']  = 'base/pagination.html'
            
            html_form = render_to_string(
                self.template_name, {'context' : context}, request)
            html_pagi = render_to_string(
                'base/pagination.html', {'context' : context}, request)
            return JsonResponse({'html': html_form, 'pagination' : html_pagi, 'total_records' : str(total_count)+' records found'})
        else:
            return super().get(request, *args, **kwargs)
        return JsonResponse(data)
        

class PostLinkTrackView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "account.view_posts"
    template_name       = 'reports/listing.html'
    model               = Posts
    

class DownloadPostLinkTrackView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'account.view_customusers'
    
    def get(self, request, *args, **kwargs):
    
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="app_data_usage.csv"'
        
        #  enterprise_id = request.session.get('auth_enterprise_id')
        filter_val = request.GET.get('keywords', '')
        
        
        
        writer = csv.writer(response)
        writer.writerow(['Title', 'description ', 'Post Type', 'User','Category','Image' 'Like Count', 'Comment Count', 'User viewed', 'Approved Status', 'Status'])
        
        filter_val = request.GET.get('keywords', '')
        
        # ~ get post data have link in Description
        post_obj = Posts.objects.extra(select={'total_count' : "SELECT count(*) FROM amrc_posts WHERE amrc_posts.id=amrc_post_reactions.post_id and amrc_post_reactions.post_track_status = True"}).filter((Q(title__icontains=filter_val) | Q(description__icontains=filter_val)),Q(is_deleted__icontains=False),Q(description__icontains='http://')).values('id', 'title', 'description','post_type','post_category__name','post_image','post_file','file_type','taggedusers','like_count','comment_count','approve_status','status','total_count','like_count','comment_count','post_image').order_by('-id')
        

        for post in post_obj:
            if post['approve_status'] == '1':
                
                approve_status = 'Approved'
            else:
                approve_status = 'Pending'
                
            if post['status'] == True:
                
                status = 'Active'
            else:
                status = 'Inactive'
            
            if post['post_image']:
                image_url = settings.BASE_URL+settings.MEDIA_URL+post['post_image']
            else:
                image_url =''
                
            writer.writerow([post['title'], post['description'], post['post_type'], post['user_id__email'], post['post_category__name'], image_url , post['like_count'], post['comment_count'], post['total_count'], approve_status, status])
            
        return response         

class PostLinkTrackAjaxView(ListView):
    model               =  Posts
    template_name       = 'reports/ajax_listing.html'
    paginate_by         = 10
    
    def get(self, request, *args, **kwargs):
        
        dict_session       = session_dict(self.request)
        # ~ auth_enterprise_id = dict_session['auth_enterprise_id']
        
        page       = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')
        # ~ and account_postsreaction.post_track_status = True
        mod_obj = Posts.objects.extra(select={'total_count' : "SELECT count(*) FROM amrc_posts WHERE amrc_posts.id=amrc_post_reactions.post_id and amrc_post_reactions.post_track_status = True"}).filter((Q(title__icontains=filter_val) | Q(description__icontains=filter_val)),Q(is_deleted__icontains=False),Q(description__icontains='http://')).values('id', 'title', 'description','post_type','post_category__name','post_image','post_file','file_type','taggedusers','like_count','comment_count','approve_status','status','total_count','like_count','comment_count').order_by('-id')
        
        total_count = mod_obj.count()
        # ~ print('total_count=>',total_count)
        if total_count == 0:
            total_count = 'No'
        paginator   = Paginator(mod_obj, self.paginate_by)
        try:
            report = paginator.page(page)
        except PageNotAnInteger:
            report = paginator.page(1)
        except EmptyPage:
            report = paginator.page(paginator.num_pages)
            
        if request.is_ajax():
            context                = dict()
            context['object_list'] = report
            context['pagination']  = 'base/pagination.html'
            
            html_form = render_to_string(
                self.template_name, {'context' : context}, request)
            html_pagi = render_to_string(
                'base/pagination.html', {'context' : context}, request)
            return JsonResponse({'html': html_form, 'pagination' : html_pagi, 'total_records' : str(total_count)+' records found'})
        else:
            return super().get(request, *args, **kwargs)
        return JsonResponse(data)
        
class PostLinkUserList(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "account.view_posts"
    template_name       = 'reports/userlist.html'
    model               = Posts
    
    def get(self, request, *args, **kwargs):
        pid = self.kwargs['token']
        return render(request,self.template_name,{'pid' : pid})
                
class PostLinkUserListAjaxView(ListView):
    model               =  Posts
    template_name       = 'reports/userlist_ajax_listing.html'
    paginate_by         = 10
    
    def get(self, request, *args, **kwargs):
        pid = self.kwargs['token']
        dict_session       = session_dict(self.request)
       
        
        page       = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')
        # ~ ,Q(post_track_status=True)
        # ~ .extra(select={'total_count' : "SELECT count(*) FROM account_postsreaction WHERE account_posts.id=account_postsreaction.post_id "})
        mod_obj = PostsReaction.objects.filter(Q(post_id=pid),Q(post_track_status=True)).values('id', 'post_id', 'user_id','user__first_name','user__last_name','user__phone').order_by('-id')
       
        
        total_count = mod_obj.count()
        # ~ print('total_count=>',total_count)
        if total_count == 0:
            total_count = 'No'
        paginator   = Paginator(mod_obj, self.paginate_by)
        try:
            report = paginator.page(page)
        except PageNotAnInteger:
            report = paginator.page(1)
        except EmptyPage:
            report = paginator.page(paginator.num_pages)
            
        if request.is_ajax():
            context                = dict()
            context['object_list'] = report
            context['pagination']  = 'base/pagination.html'
            
            html_form = render_to_string(
                self.template_name, {'context' : context}, request)
            html_pagi = render_to_string(
                'base/pagination.html', {'context' : context}, request)
            return JsonResponse({'html': html_form, 'pagination' : html_pagi, 'total_records' : str(total_count)+' records found'})
        else:
            return super().get(request, *args, **kwargs)
        return JsonResponse(data)
