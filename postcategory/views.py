from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.shortcuts import render,redirect, get_object_or_404
from django.core.paginator import Paginator
from django.template.loader import render_to_string

from .ajax_views import *
from django.http import JsonResponse
from django.db.models import Q, Count
from americana.utils import model_to_dict, timezones
from .forms import *
from americana.utils import session_dict, get_client_ip
from americana.encryption import encrypt, decrypt
from .models import PostCategory


class PostCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model               = PostCategory
    template_name       = 'postcategory/listing.html'
    permission_required = 'postcategory.delete_postcategory'
    
    def get(self, request, *args, **kwargs):
        
        context = dict()
        if request.is_ajax():
            data              = dict()
            html              = render_to_string('postcategory/deleteApp.html', context, request)
            data['html_form'] = True    
            
            return JsonResponse({'html_form': data, 'html': html})
        else:
            return render(request, 'postcategory/listing.html')

    def post(self, request, *args, **kwargs):
        dict_session = session_dict(self.request)
        updated_by=dict_session["_auth_user_id"]
        # ~ auth_slug    = dict_session['auth_user_slug']
        try :
            id      = request.POST.getlist('ids[]')
            # ~ indexes = [int(decrypt(i)) for i in id]
            indexes = [int((i)) for i in id]
            groupObj = [i.id for i in PostCategory.objects.filter(Q(is_deleted=False))]
            # ~ policyObj = [i.id for i in Enterprise_groups.objects.filter(Q(is_deleted=0,policy__isnull=True))]
            context = dict()
            data = dict()
            for i in indexes:
                
                        PostCategory.objects.filter(Q(is_deleted=False, id=i)).update(is_deleted=True, ip_address=get_client_ip(self.request), updated_by=updated_by, updatedAt=timezones())
                   
            html = render_to_string('postcategory/deleteApp.html', {'context':context}, request)
            if context:
                data['html'] = html
                data['response'] = False
                return JsonResponse(data)
                    
            else:
                url_link    = reverse_lazy('postcategory:{}'.format('postcategory'))
                data['url'] = url_link
                data['response'] = True
                data['success'] = True
                data['msg'] = 'Record Deleted Successfully'
                return JsonResponse(data, status = 200)
            
        except template.TemplateDoesNotExist:
            return render(request, 'postcategory/listing.html')

class PostCategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    
    permission_required = "postcategory.add_postcategory"
    form_class          = PostCategoryAdminCreationForm
    model               = PostCategory
    template_name       = 'postcategory/add.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST)
        return render(self.request, self.template_name, {"form": form})
    
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            dict_session  = session_dict(self.request)
            created_by    = dict_session['_auth_user_id']
            # ~ auth_slug     = dict_session['auth_user_slug']
            # ~ enterprise_id = dict_session['auth_enterprise_id']
            
            form    = self.form_class(self.request.POST)
            context = {
                'form' : form
            }
            name          = self.request.POST.get('name')
            description   = self.request.POST.get('description')
            sequence      = self.request.POST.get('sequence')
            # ~ enterprise_id = self.request.POST.get('enterprise')
            
            if form.is_valid():
               postcategory = PostCategory(name=name, description=description,sequence=sequence)
               # ~ , createdAt=timezones(), created_by=created_by, ip_address=get_client_ip(self.request), enterprise=User.objects.get(id=enterprise_id))
               postcategory.save()
               return JsonResponse({"success" : True, 'redirect_url' : reverse('postcategory:postcategory'), 'msg' : 'Category has been created successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success":False}, status=400)


class PostCategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):    
    
    permission_required = "postcategory.change_postcategory"  
    model               = PostCategory
    form_class          = PostCategoryAdminCreationForm
    template_name       = 'postcategory/edit.html'
    initial             = {'key' : 'value'}
    
    def get(self, request, *args, **kwargs):
        encrypt_pk = self.kwargs['token']
        decrypt_pk = (encrypt_pk) 
        context    = {}
        groups     = get_object_or_404(PostCategory, pk=decrypt_pk, is_deleted=False)
        dictionary = model_to_dict(PostCategory.objects.filter(pk=decrypt_pk, is_deleted=False).only('name', 'description', 'status')[0])
        
        form = self.form_class(initial=dictionary, group_id=decrypt_pk)
       
        return render(self.request, self.template_name, {"form": form, 'id' : encrypt_pk})
        
    def post(self, request, *args, **kwargs):
        if self.request.method == "POST" and self.request.is_ajax():
            encrypt_pk   = self.kwargs['token']
            decrypt_pk   = (encrypt_pk) 
            dict_session = session_dict(self.request)
            updated_by   = dict_session['_auth_user_id']
            auth_slug    = dict_session['auth_user_slug']
            
            form          = self.form_class(self.request.POST, group_id=decrypt_pk)
            name          = request.POST.get('name')
            description   = request.POST.get('description')
            sequence      = request.POST.get('sequence')
            # ~ enterprise_id = request.POST.get('enterprise')
            
            context = {
                'form' : form
            }
            if form.is_valid():
               groups = PostCategory.objects.get(id=decrypt_pk, is_deleted=False)
               
               groups.name        = name
               groups.description = description
               groups.sequence    = sequence  
               groups.updated_by  = updated_by
               groups.ip_address  = get_client_ip(self.request)
               groups.updatedAt   = timezones()
              
               groups.save()
               return JsonResponse({"success" : True, 'redirect_url' : reverse('postcategory:postcategory'), 'msg' : 'Category has been updated successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success" : False}, status=400)
    
    
    
class PostCategoryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "postcategory.view_postcategory"
    template_name       = 'postcategory/listing.html'
    model               = PostCategory

class PostCategoryAjaxView(ListView):
    model               =  PostCategory
    permission_required = "postcategory.view_postcategory"
    template_name       = 'postcategory/ajax_listing.html'
    paginate_by         = 10
    
    def get(self, request, *args, **kwargs):
        
        dict_session = session_dict(self.request)
        page       = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')
        
        mod_obj = PostCategory.objects.filter(
            Q(name__icontains=filter_val), Q(is_deleted__icontains=False)).values('id', 'name', 'description','sequence').order_by('sequence')
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
