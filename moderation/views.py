from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from .ajax_views import *
from django.http import JsonResponse
from django.db.models import Q, Count
from americana.utils import model_to_dict, timezones
from .forms import *


from americana.utils import session_dict, get_client_ip
from americana.encryption import encrypt, decrypt
from .models import Moderation


class ModerationDeleteView(LoginRequiredMixin, DeleteView):
    model               = Moderation
    template_name       = 'moderation/listing.html'
    permission_required = 'moderation.delete_moderation'
    
    def get(self, request, *args, **kwargs):
        context = dict()
        if request.is_ajax():
            try:
                html_form = render_to_string('base/confirm_delete.html', context, request)
            except:
                html_form = render_to_string('moderation/listing.html', context, request)           
    
            return JsonResponse({'html': html_form})
        else:
            return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        dict_session = session_dict(self.request)
        updated_by = dict_session['_auth_user_id']
        try :
            id = request.POST.getlist('ids[]')
            indexes = [int(decrypt(i)) for i in id]
            context = False
            data = dict()
            for i in indexes:
                context = Moderation.objects.filter(Q(is_deleted=False, id=i)).update(is_deleted=True, ip_address=get_client_ip(self.request), updated_by=updated_by, updatedAt=timezones())
            if not context:
                data['success'] = False
                data['msg'] = 'Some error has been occurred.'
                return JsonResponse(data)
            else:
                data['success'] = True
                data['msg'] = 'Word has been deleted Successfully'
                return JsonResponse(data, status = 200)
            
        except template.TemplateDoesNotExist:
            return JsonResponse({"success" : False, 'msg' : 'Some error has been occurred, please try again.'}, status = 200)


class ModerationCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    
    permission_required = "moderation.add_moderation"
    form_class          = ModerationAdminCreationForm
    model               = Moderation
    template_name       = 'moderation/add.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST)
        return render(self.request, self.template_name, {"form": form})
    
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            dict_session  = session_dict(self.request)
            created_by    = dict_session['_auth_user_id']
            
            ip_address=get_client_ip(self.request)

            form    = self.form_class(self.request.POST)
            context = {
                'form' : form
            }
            word          = self.request.POST.get('word')
            description   = self.request.POST.get('description')
            
            if form.is_valid():
               moderation = Moderation(word=word, description=description,created_by=created_by,ip_address=ip_address)
               moderation.save()
               return JsonResponse({"success" : True, 'redirect_url' : reverse('moderation:moderation'), 'msg' : 'Word has been created successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success":False}, status=400)


class ModerationUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):    
    
    permission_required = "moderation.change_moderation"  
    model               = Moderation
    form_class          = ModerationAdminCreationForm
    template_name       = 'moderation/edit.html'
    initial             = {'key' : 'value'}
    
    def get(self, request, *args, **kwargs):
        encrypt_pk = self.kwargs['token']
        decrypt_pk = (encrypt_pk) 
        decrypt_pk = decrypt(encrypt_pk) 
       
        context    = {}
        groups     = get_object_or_404(Moderation, pk=decrypt_pk, is_deleted=False)
        dictionary = model_to_dict(Moderation.objects.filter(pk=decrypt_pk, is_deleted=False).only('word', 'description', 'status')[0])
        
        form = self.form_class(initial=dictionary, group_id=decrypt_pk)
       
        return render(self.request, self.template_name, {"form": form, 'id' : encrypt_pk})
        
    def post(self, request, *args, **kwargs):
        if self.request.method == "POST" and self.request.is_ajax():
            encrypt_pk   = self.kwargs['token']
            decrypt_pk   = decrypt(encrypt_pk) 
            dict_session = session_dict(self.request)
            updated_by   = dict_session['_auth_user_id']
            auth_slug    = dict_session['auth_user_slug']
            
            form        = self.form_class(self.request.POST, group_id=decrypt_pk)
            word        = request.POST.get('word')
            description = request.POST.get('description')
            
            context = {
                'form' : form
            }
            if form.is_valid():
               groups = Moderation.objects.get(id=decrypt_pk, is_deleted=False)
               
               groups.word        = word
               groups.description = description
               groups.updated_by  = updated_by
               groups.ip_address  = get_client_ip(self.request)
               groups.updatedAt   = timezones()
              
               groups.save()
               return JsonResponse({"success" : True, 'redirect_url' : reverse('moderation:moderation'), 'msg' : 'Word has been updated successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success" : False}, status=400)
    
    
    
class ModerationListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "moderation.view_moderation"
    template_name       = 'moderation/listing.html'
    model               = Moderation


class ModerationAjaxView(ListView):
    model               =  Moderation
    permission_required = "moderation.view_moderation"
    template_name       = 'moderation/ajax_listing.html'
    paginate_by         = 10
    
    def get(self, request, *args, **kwargs):
        
        dict_session = session_dict(self.request)
        page = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')
        
        mod_obj = Moderation.objects.filter(
            Q(word__icontains=filter_val), Q(is_deleted__icontains=False)).values('id', 'word', 'description').order_by('-id')
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
