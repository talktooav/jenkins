from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin)
from django.views.generic import CreateView, View, UpdateView, ListView
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.db.models import Q
from .forms import RoleCreateForm, RoleChangeForm
from americana.encryption import decrypt
from django.conf import settings
from americana.utils import session_dict, timezones
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def permission_data(request):

    perms = {}
    for items in ContentType.objects.exclude(
         Q(model__icontains='user_login_log') |
         Q(model__icontains='useractivity') |
         Q(model__icontains='phoneotp') |
         Q(model__icontains='logentry') | Q(model__icontains='permission') |
         Q(model__icontains='contenttype') | Q(model__icontains='session')):

        if items.model == 'group':
            if request.session.get('auth_user_type') != 'admin':
                continue
            else:
                items.model = 'role'
        elif items.model == 'config':
            items.model = 'account'

        perms[items.model] = {}

        for perm_items in Permission.objects.filter(content_type=items.id):

            perm_codename = perm_items.codename

            if 'group' in perm_items.codename and items.model == 'role':
                if request.session.get('auth_user_type') != 'admin':
                    continue
            elif 'wifi_config_policy' in perm_items.codename:
                if 'change' in perm_items.codename:
                    continue
                perm_codename = perm_items.codename
            elif 'notification' in perm_items.codename:
                if 'add' in perm_items.codename or \
                   'change' in perm_items.codename:
                    continue
                perm_codename = perm_items.codename
            else:
                perm_codename = perm_items.codename

            perms[items.model][perm_items.id] = {}
            if perm_codename:
                perms[items.model][perm_items.id]['name'] = \
                 perm_codename.replace('_', ' ')
            # ~ print(perms)
        # perms[items.id].append({'name' : items.name})
    return perms


class RoleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    form_class = RoleCreateForm
    initial = {'key': 'value'}
    template_name = 'roles/add.html'
    permission_required = "auth.add_group"

    def get(self, request, *args, **kwargs):
        perms = permission_data(request)
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {
            'form': form, 'permss': perms})

    def post(self, request, *args, **kwargs):

        if self.request.method == 'POST' and self.request.is_ajax():
            dict_session = session_dict(self.request)
            created_by = dict_session['_auth_user_id']
            auth_slug = dict_session['auth_user_slug']

            form = self.form_class(request.POST)
            permissions = request.POST.getlist('permissions[]')
            group_name = request.POST.get('name')

            if form.is_valid():
                group = Group(
                    name=group_name, modified_by=created_by,
                    createdAt=timezones())
                group.save()
                group_perm = Group.objects.get(name=group_name, is_deleted=0)
                for perm_id in permissions:
                    group_perm.permissions.add(perm_id)

                return JsonResponse({
                    "success": True, 'redirect_url': reverse('roles:roles'),
                    'msg': 'Role has been created succussfully!'}, status=200)
            else:
                return JsonResponse({
                    'success': False, 'errors': form.errors.as_json()},
                    status=200)


class RoleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):

    template_name = 'roles/edit.html'
    form_class = RoleChangeForm
    initial = {'key': 'value'}
    permission_required = "auth.change_group"

    def get(self, request, *args, **kwargs):

        perms = permission_data(request)
        encrypt_pk = self.kwargs['token']
        decrypt_pk = decrypt(encrypt_pk)

        context = {}
        group = get_object_or_404(Group, pk=decrypt_pk, is_deleted=0)
        permission_arr = group.permissions.values_list('id', flat=True)

        context['name'] = group
        context['permission_arr'] = list(permission_arr)
        context['role_id'] = encrypt_pk
        return render(request, self.template_name, {
            'context': context, 'permss': perms})

    def post(self, request, *args, **kwargs):

        if self.request.method == 'POST' and self.request.is_ajax():
            encrypt_pk = self.kwargs['token']
            decrypt_pk = decrypt(encrypt_pk)
            dict_session = session_dict(self.request)
            updated_by = dict_session['_auth_user_id']

            form = self.form_class(request.POST)
            permissions_list = request.POST.getlist('permissions[]')
            name = request.POST.get('name')

            # converting in readable form
            permission_arr = [int(i) for i in permissions_list]

            # ~ context['permission_arr'] = permission_arr
            # ~ context['name']           = name
            # ~ context['role_id']        = self.kwargs['pk']

            if form.is_valid():
                group = Group.objects.get(id=decrypt_pk, is_deleted=0)
                group.name = name
                group.modified_by = updated_by
                group.updatedAt = timezones()
                group.save()

                # group_perm = group.objects.get(name=name)
                group_perm = Group.objects.get(name=name, is_deleted=0)
                # group_perm.permissions.clear() remove all permission
                # from auth_group_permissions table on basis of group
                group_perm.permissions.set(permission_arr)
                # for perm_id in permission_arr:
                #     print('perm_id', perm_id)
                #     group_perm.permissions.add(perm_id)
                return JsonResponse({
                    "success": True, 'redirect_url': reverse('roles:roles'),
                    'msg': 'Role has been updated succussfully!'}, status=200)
            else:
                return JsonResponse({
                    "success": False, 'errors': form.errors.as_json()},
                    status=200)


class RoleChangeStatus(LoginRequiredMixin, PermissionRequiredMixin, View):
    model = Group


class RoleAjaxView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Group
    template_name = 'roles/ajax_listing.html'
    paginate_by = 10
    permission_required = "auth.view_group"

    def get(self, request, *args, **kwargs):
        dict_session = session_dict(self.request)
        created_by = dict_session['_auth_user_id']

        page = request.GET.get('page', 1)
        keywords = request.GET.get('keywords', '')
        roles_obj = Group.objects.filter(
            Q(name__icontains=keywords),
            Q(is_deleted=0, modified_by=created_by)).order_by('-id')

        total_count = roles_obj.count()
        if total_count == 0:
            total_count = 'No'
        paginator = Paginator(roles_obj, self.paginate_by)
        try:
            roles = paginator.page(page)
        except PageNotAnInteger:
            roles = paginator.page(1)
        except EmptyPage:
            roles = paginator.page(paginator.num_pages)

        if request.is_ajax():
            context = dict()
            context['object_list'] = roles

            html_form = render_to_string(
                self.template_name, {'context': context}, request)
            html_pagi = render_to_string(
                'base/pagination.html', {'context': context}, request)
            return JsonResponse({
                'html': html_form, 'pagination': html_pagi,
                'total_records': str(total_count)+' records found'})
        else:
            return super().get(request, *args, **kwargs)


class RoleListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = 'roles/listing.html'
    model = Group
    paginate_by = 10
    permission_required = "auth.view_group"

    def get_queryset(self):
        
        name = self.request.GET.get('name', '')
        new_context = Group.objects.filter(
            Q(name__icontains=name),
            Q(is_deleted=0)).order_by('-id')
        return new_context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = self.request.GET.get('name', '')
        context['total'] = self.get_queryset().count()
        context['STATUS'] = settings.STATUS
        return context


class RoleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Group
    template_name = 'roles/listing.html'
    permission_required = "auth.delete_group"

    def get(self, request, *args, **kwargs):
        context = dict()
        if request.is_ajax():
            try:
                html_form = render_to_string(
                    'base/confirm_delete.html', context, request)
            except Exception:
                html_form = render_to_string(
                    'roles/listing.html', context, request)     

            return JsonResponse({'html': html_form})
        else:
            return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        ids = self.request.POST.getlist('ids[]')

        if ids:
            try:
                id = request.POST.getlist('ids[]')
                indexes = [int(decrypt(i)) for i in id]
                context = dict()

                obj = Group.objects.filter(Q(is_deleted=0, user__isnull=True))
                k = [i.id for i in obj]
                for i in indexes:
                    if i in k:
                        Group.objects.filter(
                            Q(is_deleted=0, id=i)).update(
                                is_deleted=1, updatedat=timezones())
                    else:
                        context[str(i)] = 'This role is already associated \
                        with user. firstly delete user'
                        break

                if context:
                    return JsonResponse({
                        "success": False, 'msg': 'Role has been assigned with \
                        the user, first of all, remove them.'},
                        status=200)
                else:
                    return JsonResponse({
                        "success": True,
                        'msg': 'Role has been succesfully removed.'},
                        status=200)
            except Exception:
                return JsonResponse({
                    "success": False,
                    'msg': 'Some error has been occurred, please try again.'},
                    status=200)
        else:
            return self.delete(*args, **kwargs)
