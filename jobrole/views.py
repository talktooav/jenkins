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
# ~ from users.models import User
from django.core.paginator import Paginator
from django.template.loader import render_to_string, get_template
from americana.utils import session_dict, get_client_ip
from americana.encryption import encrypt, decrypt
from .models import JobRoles

# ~ from devices.models import Devices
class JobRolesDeleteView(LoginRequiredMixin, DeleteView):
    model               = JobRoles
    template_name       = 'jobrole/listing.html'
    permission_required = 'jobrole.delete_jobroles'
    
    def get(self, request, *args, **kwargs):
        
        context = dict()
        if request.is_ajax():
            data              = dict()
            html              = render_to_string('jobrole/deleteApp.html', context, request)
            data['html_form'] = True    
            
            return JsonResponse({'html_form': data, 'html': html})
        else:
            return render(request, 'jobrole/listing.html')

    def post(self, request, *args, **kwargs):
        dict_session = session_dict(self.request)
        # ~ auth_slug    = dict_session['auth_user_slug']
        try :
            id      = request.POST.getlist('ids[]')
            # ~ indexes = [int(decrypt(i)) for i in id]
            indexes = [int((i)) for i in id]
            groupObj = [i.id for i in JobRoles.objects.filter(Q(is_deleted=False, id=i))]
            # ~ policyObj = [i.id for i in Enterprise_groups.objects.filter(Q(is_deleted=0,policy__isnull=True))]
            context = dict()
            data = dict()
            for i in indexes:
                
                        JobRoles.objects.filter(Q(is_deleted=False, id=i)).update(is_deleted=True, ip_address=get_client_ip(self.request), updated_by=updated_by, updatedAt=timezones())
                   
            html = render_to_string('jobrole/deleteApp.html', {'context':context}, request)
            if context:
                data['html'] = html
                data['response'] = False
                return JsonResponse(data)
                    
            else:
                url_link    = reverse_lazy('jobrole:{}'.format('jobrole'))
                data['url'] = url_link
                data['response'] = True
                data['success'] = True
                data['msg'] = 'Record Deleted Successfully'
                return JsonResponse(data, status = 200)
            
        except template.TemplateDoesNotExist:
            return render(request, 'jobrole/listing.html')

class JobRolesCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    
    permission_required = "jobrole.add_jobroles"
    form_class          = JobRolesAdminCreationForm
    model               = JobRoles
    template_name       = 'jobrole/add.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST)
        return render(self.request, self.template_name, {"form": form})
    
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            dict_session  = session_dict(self.request)
            created_by    = dict_session['_auth_user_id']
            brand_id = dict_session['auth_brand_id']
            # ~ auth_slug     = dict_session['auth_user_slug']
            # ~ enterprise_id = dict_session['auth_enterprise_id']
            
            form    = self.form_class(self.request.POST)
            context = {
                'form' : form
            }
            name          = self.request.POST.get('name')
            description   = self.request.POST.get('description')
            # ~ enterprise_id = self.request.POST.get('enterprise')
            
            if form.is_valid():
               jobrole = JobRoles(name=name, description=description,created_at=timezones(), created_by=created_by, ip_address=get_client_ip(self.request),brand_id=brand_id)
               # ~ , createdAt=timezones(), created_by=created_by, ip_address=get_client_ip(self.request), enterprise=User.objects.get(id=enterprise_id))
               jobrole.save()
               return JsonResponse({"success" : True, 'redirect_url' : reverse('jobrole:jobrole'), 'msg' : 'Job role has been created successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success":False}, status=400)


class JobRolesUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):    
    
    permission_required = "jobrole.change_jobroles"  
    model               = JobRoles
    form_class          = JobRolesAdminCreationForm
    template_name       = 'jobrole/edit.html'
    initial             = {'key' : 'value'}
    
    def get(self, request, *args, **kwargs):
        encrypt_pk = self.kwargs['token']
        decrypt_pk = (encrypt_pk) 
        # ~ decrypt_pk = decrypt(encrypt_pk) 
       
        context    = {}
        groups     = get_object_or_404(JobRoles, pk=decrypt_pk, is_deleted=False)
        dictionary = model_to_dict(JobRoles.objects.filter(pk=decrypt_pk, is_deleted=False).only('name', 'description', 'status')[0])
        
        form = self.form_class(initial=dictionary, group_id=decrypt_pk)
       
        return render(self.request, self.template_name, {"form": form, 'id' : encrypt_pk})
        
    def post(self, request, *args, **kwargs):
        if self.request.method == "POST" and self.request.is_ajax():
            encrypt_pk   = self.kwargs['token']
            decrypt_pk   = (encrypt_pk) 
            dict_session = session_dict(self.request)
            updated_by   = dict_session['_auth_user_id']
            auth_slug    = dict_session['auth_user_slug']
            brand_id = dict_session['auth_brand_id']
            form          = self.form_class(self.request.POST, group_id=decrypt_pk)
            name          = request.POST.get('name')
            description   = request.POST.get('description')
            # ~ enterprise_id = request.POST.get('enterprise')
            
            context = {
                'form' : form
            }
            if form.is_valid():
               groups = JobRoles.objects.get(id=decrypt_pk, is_deleted=False)
               
               groups.name        = name
               groups.description = description
               groups.updated_by  = updated_by
               groups.ip_address  = get_client_ip(self.request)
               groups.updatedAt   = timezones()
               
              
               groups.save()
               return JsonResponse({"success" : True, 'redirect_url' : reverse('jobrole:jobrole'), 'msg' : 'Job role has been updated successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success" : False}, status=400)
    
    
    
class JobRolesListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "jobrole.view_jobroles"
    template_name       = 'jobrole/listing.html'
    model               = JobRoles


class JobRolesAjaxView(ListView):
    model               =  JobRoles
    permission_required = "jobrole.view_jobroles"
    template_name       = 'jobrole/ajax_listing.html'
    paginate_by         = 10
    
    def get(self, request, *args, **kwargs):
        
        dict_session       = session_dict(self.request)
        # ~ auth_enterprise_id = dict_session['auth_enterprise_id']
        
        page       = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')
        
        mod_obj = JobRoles.objects.filter(
            Q(name__icontains=filter_val), Q(is_deleted__icontains=False)).values('id', 'name', 'description','created_at').order_by('-id')
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
