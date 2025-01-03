from django.shortcuts import render
from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin)
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from .ajax_views import *
from django.http import JsonResponse
from django.db.models import Q
from americana.utils import model_to_dict, timezones
from .forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from americana.utils import session_dict, get_client_ip
from americana.encryption import encrypt, decrypt
from .models import UserEntity


class UserEntityDeleteView(LoginRequiredMixin, DeleteView):
    model = UserEntity
    template_name = 'userentity/listing.html'
    permission_required = 'userentity.delete_userentity'

    def get(self, request, *args, **kwargs):

        context = dict()
        if request.is_ajax():
            data = dict()
            html = render_to_string(
                'userentity/deleteApp.html', context, request)
            data['html_form'] = True

            return JsonResponse({'html_form': data, 'html': html})
        else:
            return render(request, 'userentity/listing.html')

    def post(self, request, *args, **kwargs):
        dict_session = session_dict(self.request)
        updated_by = dict_session['_auth_user_id']
        try:
            id = request.POST.getlist('ids[]')
            indexes = [int((i)) for i in id]
            context = dict()
            data = dict()
            for i in indexes:
                UserEntity.objects.filter(Q(is_deleted=False, id=i)).update(is_deleted=True, ip_address=get_client_ip(self.request), updated_by=updated_by, updatedAt=timezones())

            html = render_to_string(
                'userentity/deleteApp.html', {'context': context}, request)
            if context:
                data['html'] = html
                data['response'] = False
                return JsonResponse(data)
            else:
                url_link = reverse_lazy('userentity:{}'.format('userentity'))
                data['url'] = url_link
                data['response'] = True
                data['success'] = True
                data['msg'] = 'Record Deleted Successfully'
                return JsonResponse(data, status=200)

        except template.TemplateDoesNotExist:
            return render(request, 'userentity/listing.html')


class UserEntityCreateView(
        LoginRequiredMixin, PermissionRequiredMixin, CreateView):

    permission_required = "userentity.add_userentity"
    form_class = UserEntityAdminCreationForm
    model = UserEntity
    template_name = 'userentity/add.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST)
        return render(self.request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):

        if self.request.method == "POST" and self.request.is_ajax():
            form = self.form_class(self.request.POST)

            name = self.request.POST.get('name')
            ip_address = get_client_ip(self.request)
            description = self.request.POST.get('description')
            dict_session  = session_dict(self.request)
            created_by    = dict_session['_auth_user_id']

            if form.is_valid():
                userentity = UserEntity(name=name, description=description,created_by=created_by,ip_address=ip_address)
                userentity.save()
                return JsonResponse({
                    "success": True,
                    'redirect_url': reverse('userentity:userentity'),
                    'msg': 'Entity has been created successfully.'},
                    status=200)
            else:
                return JsonResponse({
                    "success": False,
                    'errors': form.errors.as_json()}, status=200)


class UserEntityUpdateView(
        LoginRequiredMixin, PermissionRequiredMixin, UpdateView):

    permission_required = "userentity.change_userentity"
    model = UserEntity
    form_class = UserEntityAdminCreationForm
    template_name = 'userentity/edit.html'
    initial = {'key': 'value'}

    def get(self, request, *args, **kwargs):
        encrypt_pk = self.kwargs['token']
        decrypt_pk = decrypt(encrypt_pk)

        dictionary = model_to_dict(UserEntity.objects.filter(
            pk=decrypt_pk, is_deleted=False).only(
                'name', 'description', 'status')[0])

        form = self.form_class(initial=dictionary, group_id=decrypt_pk)

        return render(self.request, self.template_name, {
            "form": form, 'id': encrypt_pk})

    def post(self, request, *args, **kwargs):
        if self.request.method == "POST" and self.request.is_ajax():
            encrypt_pk = self.kwargs['token']
            decrypt_pk = (encrypt_pk)
            dict_session = session_dict(self.request)
            updated_by = dict_session['_auth_user_id']

            form = self.form_class(self.request.POST, group_id=decrypt_pk)
            name = request.POST.get('name')
            description = request.POST.get('description')

            if form.is_valid():
                groups = UserEntity.objects.get(
                    id=decrypt_pk, is_deleted=False)

                groups.name = name
                groups.description = description
                groups.updated_by = updated_by
                groups.ip_address = get_client_ip(self.request)
                groups.updatedAt = timezones()
                groups.save()

                return JsonResponse({
                    "success": True,
                    'redirect_url': reverse('userentity:userentity'),
                    'msg': 'Entity has been updated successfully.'},
                    status=200)
            else:
                return JsonResponse({
                    "success": False,
                    'errors': form.errors.as_json()}, status=200)


class UserEntityListView(
        LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = "userentity.view_userentity"
    template_name = 'userentity/listing.html'
    model = UserEntity


class UserEntityAjaxView(ListView):
    model = UserEntity
    permission_required = "userentity.view_userentity"
    template_name = 'userentity/ajax_listing.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):

        page = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')

        mod_obj = UserEntity.objects.filter(
            Q(name__icontains=filter_val),
            Q(is_deleted__icontains=False)).values(
                'id', 'name', 'description', 'createdAt').order_by('-id')
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
            context = dict()
            context['object_list'] = devices
            context['pagination'] = 'base/pagination.html'

            html_form = render_to_string(
                self.template_name, {'context': context}, request)
            html_pagi = render_to_string(
                'base/pagination.html', {'context': context}, request)
            return JsonResponse({
                'html': html_form,
                'pagination': html_pagi,
                'total_records': str(total_count)+' records found'})
        else:
            return super().get(request, *args, **kwargs)
