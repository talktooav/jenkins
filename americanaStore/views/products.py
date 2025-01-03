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
from americanaStore.models import Products
import json
from americanaStore.forms import *
from americana.files import file_upload
from django.conf import settings

PRODUCT_IMAGE_LOCATION = '/root/americana/Americana/americana/static_cdn/upload_media/americanaStore/products/image/'
PRODUCT_IMAGE_UPLOAD_PATH = '/media/americanaStore/products/image/'

# class ProductDeleteView(LoginRequiredMixin, DeleteView):
#     model               = Products
#     template_name       = 'product/listing.html'
#     permission_required = 'products.delete_products'
    
#     def get(self, request, *args, **kwargs):
        
#         context = dict()
#         if request.is_ajax():
#             try:
#                 html_form = render_to_string(
#                     'base/confirm_delete.html', context, request)
#             except Exception:
#                 html_form = render_to_string(
#                     'products/listing.html', context, request)
#             return JsonResponse({'html': html_form})
#         else:
#             return super().get(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         dict_session = session_dict(self.request)
#         updated_by = dict_session['_auth_user_id']
#         try :
#             id = request.POST.getlist('ids[]')
#             indexes = [int((i)) for i in id]
#             groupObj = [i.id for i in Products.objects.filter(Q(is_deleted=False))]
#             context = dict()
#             data = dict()
#             for i in indexes:
#                 Products.objects.filter(Q(is_deleted=False,id=i)).update(is_deleted=True, updated_by=updated_by)
            
#             return JsonResponse({"success": True, 'msg': 'Product has been successfully deleted.'}, status=200)
                
#         except Exception:
#             return JsonResponse({"success": False, 'msg': 'Some error has been occurred, please try again.'}, status=200)


class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    
    permission_required = "quiz.add_quizes"
    form_class          = ProductAdminCreationForm
    model               = Products
    template_name       = 'americanaStore/add.html'
    
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
            price = self.request.POST.get('price')
            description = self.request.POST.get('description')
            image_json = dict()
            product_image = request.FILES['upldFile']
            if product_image:
                upload_image = file_upload(product_image, PRODUCT_IMAGE_LOCATION, PRODUCT_IMAGE_UPLOAD_PATH) 
                if upload_image == False:
                    return JsonResponse({"success" : False, 'msg' : 'Some error has been occurred for upload he post image, please try again.'}, status=200)
                else:
                    image_json['fileURL']  = settings.BASE_URL+upload_image['upload_url']
                    image_json['fileHash'] = upload_image['hash']
                    image_json['fileSize'] = upload_image['size']

            post_image = image_json
            if form.is_valid():
                logo = False
                product = Products(
                        name = name,
                        price=price,
                        product_image=image_json,
                        description=description,
                        ip_address = ip_address,
                        created_by = created_by,
                        createdAt = timezones(),
                        brand_id = auth_brand_id
                )
                product.save()
                
                return JsonResponse({"success" : True, 'redirect_url' : reverse('americanaStore:product'), 'msg' : 'Product has been saved successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success":False}, status=400)


class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):    
    
    permission_required = "quiz.change_quizes"  
    model               = Products
    form_class          = ProductAdminCreationForm
    template_name       = 'americanaStore/edit.html'
    initial             = {'key' : 'value'}
    
    def get(self, request, *args, **kwargs):
        encrypt_pk = self.kwargs['token']
        decrypt_pk = decrypt(encrypt_pk) 
        # ~ groups  = get_object_or_404(Quizes, pk=decrypt_pk, is_deleted=False)
        dictionary = model_to_dict(Products.objects.filter(pk=decrypt_pk, is_deleted=False).only('name', 'description', 'price')[0])
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
            description = self.request.POST.get('description')
            price = self.request.POST.get('price')
            
            if form.is_valid():
                Products.objects.filter(id=decrypt_pk).update(name=name, description=description,price=price, updatedAt=timezones(), ip_address=get_client_ip(self.request))
                return JsonResponse({"success" : True, 'redirect_url' : reverse('americanaStore:product'), 'msg' : 'Product has been updated successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success" : False}, status=400)
        
    
class ProductListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "quiz.view_quizes"
    template_name       = 'americanaStore/listing.html'
    model               = Products


class ProductAjaxView(ListView):
    model               =  Products
    permission_required = "quiz.view_quizes"
    template_name       = 'americanaStore/ajax_listing.html'
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
        mod_obj = Products.objects.filter(brand_filter).values('id', 'name', 'description', 'price', 'product_image', 'createdAt').order_by('-id')
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
