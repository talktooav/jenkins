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
from americanaStore.models import JobUserStore
import json
from django.conf import settings

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

    
class UserStoreListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "quiz.view_quizes"
    template_name       = 'americanaStore/userStore/listing.html'
    model               = JobUserStore


class UserStoreAjaxView(ListView):
    model               =  JobUserStore
    permission_required = "quiz.view_quizes"
    template_name       = 'americanaStore/userStore/ajax_listing.html'
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
        mod_obj = JobUserStore.objects.filter(is_deleted=False).values('user__employee_name', 'user__employee_code', 'product__name' ,'product__product_image','boughtAt').order_by('-id')
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