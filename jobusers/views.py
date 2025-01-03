from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.views.generic import DetailView, View, UpdateView, ListView, DeleteView
from django.shortcuts import render, redirect
from americana.utils import model_to_dict, session_dict, get_client_ip, timezones
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q
from .forms import *
from americana.utils import session_dict, get_client_ip
from .models import JobUsers
# ~ from mdm.encryption import encrypt, decrypt
from django.db import IntegrityError, transaction
import pandas as pd
import csv
from django.contrib import messages

#LoginRequiredMixin,
class UsersHomeView(LoginRequiredMixin, DetailView):
    template_name = 'users/home.html'
    def get_object(self):
        return self.request.user
        
        

class jobUserUploadView(LoginRequiredMixin, UpdateView):
    # declaring template
    # ~ template = "profile_upload.html"
    data = JobUsers.objects.all()
    
    # prompt is a context variable that e thae  tthacan have different values      depending on their context
    prompt = {
        'order': 'Order of the CSV should be name, email, address, phone, profile',
        'profiles': data    
              }
      
    # GET request returns the value of the data with the specified key.
    # ~ if request.method == "GET":
        # ~ return render(request, template, prompt)
    def post(self,request , *args, **kwargs):
       
        dict_session = session_dict(self.request)
        created_by = dict_session['_auth_user_id']
        auth_brand_id = dict_session['auth_brand_id']
        ip_address = get_client_ip(self.request)
        
        csv_file = request.FILES['file']
        # let's check if it is a csv file
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'THIS IS NOT A CSV FILE')
            return redirect(reverse('jobusers:jobusers'))
   
        df = pd.read_csv(csv_file)
        dataframe =  ['Market','City','EMP CODE','EMPLOYEE NAME','JOB NAME','Gender','NATIONALITY','D.O.B','HIRE DATE','CC CODE','COST NAME']
        column = list(df.columns.values) 
        error_list = '' 
        count = 0
        for i in column :
            if not i in dataframe:
                count+=1
                error_list = error_list+' '+i+','
        if count!=0:
            messages.error(request, '{} column name is wrong. it must be column name like {} format.'.format(error_list,dataframe))
            return redirect(reverse('jobusers:jobusers'))
        
        job_roles   = JobRoles.objects.filter(status=True, is_deleted=False)
        job_role_id = {}
        for job_role_data in job_roles:
            job_role_id[job_role_data.name] = job_role_data.id
        
        for i in range(0,df.shape[0]):
            if df.iloc[i]['EMP CODE'] and df.iloc[i]['JOB NAME'] and df.iloc[i]['Market'] and df.iloc[i]['D.O.B']:
                
                dateOfBirth           = df.iloc[i]['D.O.B'] 
                dateOfBirth           = dateOfBirth.split('/') 
                if str(df.iloc[i]['D.O.B'])!= 'nan':
                    dateOfBirth = df.iloc[i]['D.O.B'] 
                    if '/' in dateOfBirth: 
                        dateOfBirth = dateOfBirth.split('/') 
                        dateOfBirth = dateOfBirth[2]+'-'+dateOfBirth[0]+'-'+dateOfBirth[1]
                    
                else:
                    dateOfBirth = ''
                        
                if str(df.iloc[i]['HIRE DATE']) != 'nan':
                    hire_date = df.iloc[i]['HIRE DATE'] 
                    # ~ hire_date = hire_date.split('/') 
                    # ~ hire_date = hire_date[2]+'-'+hire_date[0]+'-'+hire_date[1] 
                else:
                    hire_date = ''
                
                
                market        = df.iloc[i]['Market']
                city          = df.iloc[i]['City']
                employee_name = df.iloc[i]['EMPLOYEE NAME']
                employee_code = df.iloc[i]['EMP CODE']
                date_of_birth = dateOfBirth
                gender        = df.iloc[i]['Gender']
                nationality   = df.iloc[i]['NATIONALITY']
                hire_date     = hire_date
                cc_code       = df.iloc[i]['CC CODE']
                cost_name     = df.iloc[i]['COST NAME']
                if df.iloc[i]['JOB NAME'] in job_role_id:
                    job_role = job_role_id[df.iloc[i]['JOB NAME']]
                else:
                    job_role = ''
                
                try:
                    with transaction.atomic():                                
                        # ~ user_insert, created = JobUsers.objects.update_or_create(city=city, employee_name=employee_name, cost_name=cost_name, hire_date=hire_date, gender=gender, cc_code=cc_code, market=market, nationality=nationality, date_of_birth=date_of_birth, job_role_id=job_role, employee_code=employee_code, is_active=True, ip_address=ip_address, created_by=created_by, brand_id=auth_brand_id, createdAt=timezones())
                        user_insert, created = JobUsers.objects.update_or_create(city=city, employee_name=employee_name, cost_name=cost_name, hire_date=hire_date, gender=gender, cc_code=cc_code, market=market, nationality=nationality, date_of_birth=date_of_birth, job_role_id=job_role, employee_code=employee_code, brand_id=auth_brand_id, created_by=created_by, defaults={'is_active': True, 'ip_address': ip_address, 'updatedAt': timezones()})
                        if created: 
                            print('The object was created')
                        else:
                            print('The object was updated')
                        created_id = user_insert.id
                        
                except IntegrityError:
                    pass
        return redirect(reverse('jobusers:jobusers'))            
                    
   
class JobUserAjaxView(ListView):
    model               = JobUsers
    template_name       = 'jobusers/ajax_listing.html'
    paginate_by         = 10
    permission_required = "jobusers.view_jobusers"
    
    def get(self, request, *args, **kwargs):
        
        dict_session = session_dict(self.request)
        auth_role = dict_session['auth_user_role']
        auth_brand_id = int(dict_session['auth_brand_id'])
        
        page = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')
        
        if auth_brand_id:
            brand_filter = Q(is_active=True, brand_id=auth_brand_id)
        else:
            brand_filter = Q(is_active=True)
            
        user_obj = JobUsers.objects.filter(
            Q(employee_code__icontains=filter_val) | Q(employee_name__icontains=filter_val),
            brand_filter
        ).order_by('-id').values('id', 'market', 'city', 'employee_name', 'employee_code', 'job_role__name', 'createdAt')
        
        total_count = user_obj.count()
        if total_count == 0:
            total_count = 'No'
        paginator   = Paginator(user_obj, self.paginate_by)
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
    

class JobUserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    template_name       = 'jobusers/listing.html'
    model               = JobUsers
    permission_required = "jobusers.view_jobusers"


class JobUserRegisterView(LoginRequiredMixin, PermissionRequiredMixin, View):
    form_class          = JobUserRegisterForm
    initial             = {'key' : 'value'}
    template_name       = 'jobusers/add.html'
    permission_required = "jobusers.add_jobusers"

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form' : form})

    def post(self, request, *args, **kwargs):
        if self.request.method == "POST" and self.request.is_ajax():
            
            dict_session = session_dict(self.request)
            created_by   = dict_session['_auth_user_id']
            ip_address= get_client_ip(self.request)
            brand_id = dict_session['auth_brand_id']
            form = self.form_class(request.POST,request.FILES)
            # user.market=request.POST.get("market")
            
            if form.is_valid():
                logo = False
                # jobusers = JobUsers(market=market,ip_address=ip_address,created_by=created_by)
                # jobusers.save()
                form.save()
                
                return JsonResponse({"success" : True, 'redirect_url' : reverse('jobusers:jobusers'), 'msg' : 'Record has been submit successfully'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
            
            return JsonResponse({"success":False}, status=400) 
       
        
class JobUserProfileUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model               = JobUsers
    form_class          = JobUserAdminChangeForm
    template_name       = 'jobusers/edit.html'
    permission_required = "jobusers.change_jobusers"
    user_idd		    = None
    
    def get(self, request, *args, **kwargs):
        encrypt_pk = self.kwargs['token']
        decrypt_pk = decrypt(encrypt_pk) 
        
        dictionary = model_to_dict(JobUsers.objects.filter(pk=decrypt_pk)[0])
        userr = dict({"user" : encrypt_pk})
        
        merge      = {**dictionary, **userr}
        form = self.form_class(initial = merge)
        return render(self.request, self.template_name, {"form": form, 'id' : encrypt_pk})
    	                
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
        
            encrypt_pk   = self.kwargs['token']
            decrypt_pk   = decrypt(encrypt_pk) 
            dict_session = session_dict(self.request)
            updated_by   = dict_session['_auth_user_id']
            auth_slug    = dict_session['auth_user_slug']
            market=request.POST.get("market")
            user = JobUsers.objects.get(id=decrypt_pk)
                
            form = self.form_class(self.request.POST, request.FILES)
            
            employee_name = request.POST.get('employee_name')
            # ~ phone = request.POST.get('phone')   
            # ~ status = request.POST.get('status')   
            dob = request.POST.get('date_of_birth')   
            gender = request.POST.get('gender')   
            employee_code = request.POST.get('employee_code')   
            # ~ email = request.POST.get('email')   
            entity_id = request.POST.get('entity')   
            new_password = request.POST.get('password')   
            
            ipaddress=get_client_ip(self.request)

            if form.is_valid():
                
                # ~ user.set_password('{}'.format(new_password))
                if new_password:
                    user.password = new_password
                user.employee_name = employee_name
                # ~ user.phone = phone
                # ~ user.status = status
                user.date_of_birth = dob
                user.employee_code = employee_code
                # ~ user.email = email
                user.entity_id = entity_id
                user.ip_address=ipaddress
                user.gender = gender
                user.market=market
                user.updated_by=updated_by
                user.save()
                
                return JsonResponse({"success" : True, 'redirect_url' : reverse('jobusers:jobusers'), 'msg' : 'User has been updated successfully.'}, status=200)
                  
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success" : False}, status=400)


class JobUserDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model               = JobUsers
    template_name       = 'jobusers/del_user.html'
    success_url         = reverse_lazy('users:users')
    permission_required = "jobusers.delete_jobusers"
    
    def get(self, request, *args, **kwargs):
       
        context = dict()
        if request.is_ajax():
            data              = dict()
            html              = render_to_string('users/deleteApp.html', context, request)
            data['html_form'] = True
              
            return JsonResponse({'html_form': data,'html':html})
        else:
            return render(request,'jobusers/listing.html')

    def post(self, request, *args, **kwargs):
        dict_session = session_dict(self.request)
        updated_by   = dict_session['_auth_user_id']
       
        try :
            id      = self.request.POST.getlist('ids[]')
            indexes = [int(decrypt(i)) for i in id]
            
            obj = User.objects.filter(is_deleted=0,enterprise_groups__isnull=True)
            k = [(i.id) for i in obj]
            context = dict()
            data = dict()
            l = 0
            for i in indexes:
                if i in k:
                    User.objects.filter(Q(is_deleted=False, id=i)).update(is_deleted=True, ip_address=get_client_ip(self.request), updated_by=updated_by, updatedAt=timezones())
                    l=l+1
            if l!=len(k):
                context[str(i)] = 'This user is already associated with group. firstly delete group'

                
            html = render_to_string('users/deleteApp.html', {'context':context}, request)
            if context:
                data['html'] = html
                data['response'] = False
                return JsonResponse(data)

            else:
                url_link    = reverse('users:home', args=(auth_slug,))
                data['url'] = url_link
                data['response'] = True
                return JsonResponse(data, status = 200)
           
        except :
            return render(request, 'users/listing.html')
