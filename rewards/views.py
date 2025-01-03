from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, FormView, UpdateView, ListView, DeleteView
from django.shortcuts import render,redirect, get_object_or_404
from django.core.paginator import Paginator
from django.template.loader import render_to_string, get_template
from django.http import JsonResponse
from django.db.models import Q, Count
from .forms import *

from americana.utils import session_dict, get_client_ip, model_to_dict, timezones, unique_slug_generator
from americana.encryption import encrypt, decrypt
from rewards.models import StarOfTheMonth,Store


class RewardsDeleteView(LoginRequiredMixin, DeleteView):
    model               = StarOfTheMonth
    template_name       = 'rewards/listing.html'
    permission_required = 'rewards.delete_starofthemonth'
    
    def get(self, request, *args, **kwargs):
        
        context = dict()
        if request.is_ajax():
            data              = dict()
            html              = render_to_string('rewards/deleteApp.html', context, request)
            data['html_form'] = True    
            
            return JsonResponse({'html_form': data, 'html': html})
        else:
            return render(request, 'rewards/listing.html')

    def post(self, request, *args, **kwargs):
        dict_session = session_dict(self.request)
        updated_by=dict_session["_auth_user_id"]
        # ~ auth_slug    = dict_session['auth_user_slug']
        try :
            id      = request.POST.getlist('ids[]')
            # ~ indexes = [int(decrypt(i)) for i in id]
            indexes = [int((i)) for i in id]
            groupObj = [i.id for i in StarOfTheMonth.objects.filter(Q(is_deleted=False))]
            # ~ policyObj = [i.id for i in Enterprise_groups.objects.filter(Q(is_deleted=0,policy__isnull=True))]
            context = dict()
            data = dict()
            for i in indexes:
                StarOfTheMonth.objects.filter(Q(is_deleted=False, id=i)).update(is_deleted=True, ip_address=get_client_ip(self.request), updated_by=updated_by, updatedAt=timezones())
                   
            html = render_to_string('rewards/deleteApp.html', {'context':context}, request)
            if context:
                data['html'] = html
                data['response'] = False
                return JsonResponse(data)
                    
            else:
                url_link    = reverse_lazy('rewards:{}'.format('rewards'))
                data['url'] = url_link
                data['response'] = True
                data['success'] = True
                data['msg'] = 'Record Deleted Successfully'
                return JsonResponse(data, status = 200)
            
        except template.TemplateDoesNotExist:
            return render(request, 'rewards/listing.html')


class RewardsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    
    permission_required = "rewards.add_starofthemonth"
    form_class          = RewardsAdminCreationForm
    model               = StarOfTheMonth
    template_name       = 'rewards/add.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST)
        return render(self.request, self.template_name, {"form": form})
    
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            dict_session  = session_dict(self.request)
            created_by    = dict_session['_auth_user_id']
            # ~ auth_slug     = dict_session['auth_user_slug']
            brand_id = dict_session['auth_brand_id']
            
            form    = self.form_class(self.request.POST)
            context = {
                'form' : form
            }
            title = self.request.POST.get('title')
            user_id = self.request.POST.get('user')
            store_id = self.request.POST.get('store')
            from_date = self.request.POST.get('from_date')
            end_date = self.request.POST.get('end_date')
            # selected_date = self.request.POST.get('selected_date')
            # award_lebel = self.request.POST.get('award_lebel')
            
            if form.is_valid():
               rewards = StarOfTheMonth(title=title, user_id=user_id,store_id=store_id ,from_date=from_date,end_date=end_date,createdAt=timezones(), ip_address=get_client_ip(self.request), brand_id=brand_id)
               rewards.save()
               return JsonResponse({"success" : True, 'redirect_url' : reverse('rewards:rewards'), 'msg' : 'Reward has been created successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success":False}, status=400)


class RewardsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):    
    
    permission_required = "rewards.change_starofthemonth"  
    model               = StarOfTheMonth
    form_class          = RewardsAdminCreationForm
    template_name       = 'rewards/edit.html'
    initial             = {'key' : 'value'}
    
    def get(self, request, *args, **kwargs):
        encrypt_pk = self.kwargs['token']
        decrypt_pk = decrypt(encrypt_pk) 
       
        context = {}
        groups = get_object_or_404(StarOfTheMonth, pk=decrypt_pk, is_deleted=False)
        dictionary = model_to_dict(StarOfTheMonth.objects.filter(pk=decrypt_pk, is_deleted=False).only('word', 'description', 'status')[0])
        
        form = self.form_class(initial=dictionary)
       
        return render(self.request, self.template_name, {"form": form, 'id' : encrypt_pk})
        
    def post(self, request, *args, **kwargs):
        if self.request.method == "POST" and self.request.is_ajax():
            encrypt_pk = self.kwargs['token']
            decrypt_pk = decrypt(encrypt_pk) 
            dict_session = session_dict(self.request)
            updated_by = dict_session['_auth_user_id']
            auth_slug = dict_session['auth_user_slug']
            brand_id = dict_session['auth_brand_id']
            
            form = self.form_class(self.request.POST, group_id=decrypt_pk)
            title = self.request.POST.get('title')
            user_id = self.request.POST.get('user')
            store_id = self.request.POST.get('store')
            from_date = self.request.POST.get('from_date')
            end_date = self.request.POST.get('end_date')
            
            if form.is_valid():
                StarOfTheMonth.objects.filter(id=decrypt_pk).update(title=title,user_id=user_id,store_id=store_id ,from_date=from_date,end_date=end_date, updated_by=updated_by, updatedAt=timezones(), ip_address=get_client_ip(self.request))
                return JsonResponse({"success" : True, 'redirect_url' : reverse('rewards:rewards'), 'msg' : 'Reward has been updated successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success" : False}, status=400)
    
    
class RewardsListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "rewards.view_starofthemonth"
    template_name       = 'rewards/listing.html'
    model               = StarOfTheMonth


class RewardsAjaxView(ListView):
    model               =  StarOfTheMonth
    permission_required = "rewards.view_starofthemonth"
    template_name       = 'rewards/ajax_listing.html'
    paginate_by         = 10
    
    def get(self, request, *args, **kwargs):
        
        dict_session = session_dict(self.request)
        page = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')
        
        mod_obj = StarOfTheMonth.objects.filter(
            Q(title__icontains=filter_val)).values('id', 'title', 'user__employee_name','user__employee_code','store__name','store__store_id').order_by('-id')
        total_count = mod_obj.count()
       
        if total_count == 0:
            total_count = 'No'
        paginator = Paginator(mod_obj, self.paginate_by)
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

class PointsDeleteView(LoginRequiredMixin, DeleteView):
    model               = StarOfTheMonth
    template_name       = 'rewards/listing.html'
    permission_required = 'rewards.delete_points'
    
    def get(self, request, *args, **kwargs):
        context = dict()
        if request.is_ajax():
            try:
                html_form = render_to_string(
                    'base/confirm_delete.html', context, request)
            except Exception:
                html_form = render_to_string(
                    'rewards/points/listing.html', context, request)
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
            obj = Points.objects.filter(Q(id__in=indexes))

            if obj:
                obj.delete()
                return JsonResponse({
                    "success": True,
                    'msg': 'Points has been successfully deleted.'},
                     status=200)
                
            # ~ except Exception:
                # ~ return JsonResponse({
                    # ~ "success": False,
                    # ~ 'msg': 'Some error has been occurred, please try again.'},
                     # ~ status=200)
        else:
            return self.delete(*args, **kwargs)


class PointsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    
    permission_required = "rewards.add_points"
    form_class          = PointsAdminCreationForm
    model               = Points
    template_name       = 'rewards/points/add.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST)
        return render(self.request, self.template_name, {"form": form})
    
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            dict_session = session_dict(self.request)
            created_by = dict_session['_auth_user_id']
            brand_id = dict_session['auth_brand_id']
            # ~ auth_slug     = dict_session['auth_user_slug']
            
            form = self.form_class(self.request.POST)
            context = {
                'form' : form
            }
            title = self.request.POST.get('title')
            points = self.request.POST.get('points')
            slug = unique_slug_generator(Points, title)
            
            if form.is_valid():
               reward_point = Points(title=title, slug=slug, points=points, createdAt=timezones(), created_by=created_by, ip_address=get_client_ip(self.request), brand_id=brand_id)
               reward_point.save()
               return JsonResponse({"success" : True, 'redirect_url' : reverse('rewards:points'), 'msg' : 'Points has been added successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success":False}, status=400)


class PointsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):    
    
    permission_required = "rewards.change_points"  
    model               = Points
    form_class          = PointsAdminCreationForm
    template_name       = 'rewards/points/edit.html'
    initial             = {'key': 'value'}
    
    def get(self, request, *args, **kwargs):
        encrypt_pk = self.kwargs['token']
        decrypt_pk = decrypt(encrypt_pk) 
        context = {}
        # ~ groups     = get_object_or_404(StarOfTheMonth, pk=decrypt_pk, is_deleted=False)
        dictionary = model_to_dict(Points.objects.filter(pk=decrypt_pk).only('title')[0])
        
        form = self.form_class(initial=dictionary)
       
        return render(self.request, self.template_name, {"form": form, 'id' : encrypt_pk})
        
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            encrypt_pk = self.kwargs['token']
            decrypt_pk = decrypt(encrypt_pk) 
            dict_session = session_dict(self.request)
            updated_by = dict_session['_auth_user_id']
            auth_slug = dict_session['auth_user_slug']
            auth_brand_id = dict_session['auth_brand_id']
            
            form = self.form_class(self.request.POST, point_id=decrypt_pk)
            title = request.POST.get('title')
            points = request.POST.get('points')
            # ~ slug = unique_slug_generator(Points, title)
            
            context = {
                'form' : form
            }
            if form.is_valid():
               groups = Points.objects.get(id=decrypt_pk)
               
               groups.title = title
               # ~ groups.slug = slug
               groups.points = points
               groups.updated_by = updated_by
               groups.ip_address = get_client_ip(self.request)
               groups.updatedAt = timezones()
               groups.brand_id = auth_brand_id
              
               groups.save()
               return JsonResponse({"success" : True, 'redirect_url' : reverse('rewards:points'), 'msg' : 'Points has been updated successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success" : False}, status=400)
    
    
class PointsListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "rewards.view_points"
    template_name       = 'rewards/points/listing.html'
    model               = Points


class PointsAjaxView(ListView):
    model               =  StarOfTheMonth
    permission_required = "rewards.view_points"
    template_name       = 'rewards/points/ajax_listing.html'
    paginate_by         = 10
    
    def get(self, request, *args, **kwargs):
        
        dict_session = session_dict(self.request)
        page = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')
        
        mod_obj = Points.objects.filter(
            Q(title__icontains=filter_val)).values('id', 'title', 'points', 'createdAt').order_by('-id')
        total_count = mod_obj.count()
       
        if total_count == 0:
            total_count = 'No'
        paginator = Paginator(mod_obj, self.paginate_by)
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

class StoresDeleteView(LoginRequiredMixin, DeleteView):
    model               = Store
    template_name       = 'rewards/listing.html'
    permission_required = 'rewards.delete_points'
    
    def get(self, request, *args, **kwargs):
        context = dict()
        if request.is_ajax():
            try:
                html_form = render_to_string(
                    'base/confirm_delete.html', context, request)
            except Exception:
                html_form = render_to_string(
                    'rewards/points/listing.html', context, request)
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
            obj = Stores.objects.filter(Q(id__in=indexes))

            if obj:
                obj.delete()
                return JsonResponse({
                    "success": True,
                    'msg': 'Store has been successfully deleted.'},
                     status=200)
                
            # ~ except Exception:
                # ~ return JsonResponse({
                    # ~ "success": False,
                    # ~ 'msg': 'Some error has been occurred, please try again.'},
                     # ~ status=200)
        else:
            return self.delete(*args, **kwargs)


class StoresCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    
    permission_required = "rewards.add_stores"
    form_class          = StoresAdminCreationForm
    model               = Store
    template_name       = 'rewards/stores/add.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST)
        return render(self.request, self.template_name, {"form": form})
    
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            dict_session  = session_dict(self.request)
            form = self.form_class(self.request.POST,request.FILES)

            created_by    = dict_session['_auth_user_id']
            brand_id = dict_session['auth_brand_id']
            
            name = self.request.POST.get('name')
            store_id = self.request.POST.get('store_id')
            print("inside stores data")

            if form.is_valid():
               stores = Store(name=name, store_id=store_id,createdAt=timezones(), ip_address=get_client_ip(self.request), brand_id=brand_id)

               stores.save()
               return JsonResponse({"success" : True, 'redirect_url' : reverse('rewards:stores'), 'msg' : 'Reward has been created successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success":False}, status=400)


class StoresUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):    
    
    permission_required = "rewards.change_points"  
    model               = Store
    form_class          = StoresAdminCreationForm
    template_name       = 'rewards/stores/edit.html'
    initial             = {'key': 'value'}
    
    def get(self, request, *args, **kwargs):
        encrypt_pk = self.kwargs['token']
        decrypt_pk = decrypt(encrypt_pk) 
        context = {}
        # ~ groups     = get_object_or_404(StarOfTheMonth, pk=decrypt_pk, is_deleted=False)
        dictionary = model_to_dict(Points.objects.filter(pk=decrypt_pk).only('title')[0])
        
        form = self.form_class(initial=dictionary)
       
        return render(self.request, self.template_name, {"form": form, 'id' : encrypt_pk})
        
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            encrypt_pk = self.kwargs['token']
            decrypt_pk = decrypt(encrypt_pk) 
            dict_session = session_dict(self.request)
            updated_by = dict_session['_auth_user_id']
            auth_slug = dict_session['auth_user_slug']
            auth_brand_id = dict_session['auth_brand_id']
            
            form = self.form_class(self.request.POST, point_id=decrypt_pk)
            name = request.POST.get('name')
            store_id = request.POST.get('store_id')
            # ~ slug = unique_slug_generator(Points, title)
            
            context = {
                'form' : form
            }
            if form.is_valid():
               groups = Store.objects.get(id=decrypt_pk)
               
               groups.name = name
               # ~ groups.slug = slug
               groups.store_id = store_id
               groups.updated_by = updated_by
               groups.ip_address = get_client_ip(self.request)
               groups.updatedAt = timezones()
               groups.brand_id = auth_brand_id
              
               groups.save()
               return JsonResponse({"success" : True, 'redirect_url' : reverse('rewards:stores'), 'msg' : 'Points has been updated successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success" : False}, status=400)
    
    
class StoresListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "rewards.view_points"
    template_name       = 'rewards/stores/listing.html'
    model               = Store


class StoresAjaxView(ListView):
    model               =  Store
    permission_required = "rewards.view_starofthemonth"
    template_name       = 'rewards/stores/ajax_listing.html'
    paginate_by         = 10
    
    def get(self, request, *args, **kwargs):
        
        dict_session = session_dict(self.request)
        page = request.GET.get('page', 1)
        auth_brand_id = dict_session['auth_brand_id']
        
        if auth_brand_id:
            brand_filter = Q(brand_id=auth_brand_id)
        else:
            brand_filter = Q(is_deleted=False)
        
        mod_obj = Store.objects.filter(brand_filter).values('id', 'name', 'store_id','createdAt').order_by('-id')
        total_count = mod_obj.count()
       
        if total_count == 0:
            total_count = 'No'
        paginator = Paginator(mod_obj, self.paginate_by)
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