from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin)
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import FormView, View, UpdateView, ListView
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from americana.utils import (
    model_to_dict, session_dict, get_client_ip,
    unique_slug_generator, timezones
)
import json
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q
from americana.mixins import NextUrlMixin, RequestFormAttachMixin
from .forms import *
from .models import User, User_Login_Log
from americana.encryption import decrypt


class LoginView(NextUrlMixin, RequestFormAttachMixin, FormView):
    form_class = LoginForm
    success_url = '/'
    template_name = 'login.html'
    default_next = '/dashboard'

    def get(self, request):
        # check if user is already logged in
        if request.user.is_authenticated:
            user_slug = self.request.session['auth_user_slug']
            # next_path = '/'+user_slug+'/dashboard'
            next_path = '/dashboard'
            return redirect(next_path)

        form = self.form_class(self.request)
        return render(request, self.template_name, {'form': form})

    def form_valid(self, form):
        var = self.request.session.items()
        user_id = list(var)[0][1]
        
        user_logo = ''
        brand_id = 0
        user_slug = 'admin'
        
        # ~ obj_user = User.objects.filter(
        # Q(id=user_id, groups__name='Enterprise', is_deleted=0))
        obj_user = User.objects.filter(
            Q(id=user_id, is_deleted=0)).values(
                'id', 'is_superuser', 'groups__name', 'slug',
                'user_logo', 'last_login_json',
                'user_type', 'created_by')
        user_role = obj_user[0]['groups__name']
        superuser = obj_user[0]['is_superuser']
        user_type = 'admin' if obj_user[0]['user_type'] == None else obj_user[0]['user_type']
        # ~ print('type', user_type)
        # ~ if user_role=='Enterprise':
        if user_type == 'brand':
            brand_id = user_id
            logo = json.dumps(str(obj_user[0]['user_logo']))
            user_slug = obj_user[0]['slug']
            if logo:
                user_logo = logo.replace('"', '')
        elif user_type == 'sub-brand':
            user_slug = obj_user[0]['slug']
            brand_id = obj_user[0]['created_by']
            obj_user_ent = User.objects.filter(
                Q(id=brand_id, is_deleted=0)).values('user_logo')
            logo = json.dumps(str(obj_user_ent[0]['user_logo']))

            if logo:
                user_logo = logo.replace('"', '')
        else:
            last_login_json = obj_user[0]['last_login_json']
            if last_login_json:
                if 'last_brand' in last_login_json:
                    brand_login_user = last_login_json['last_brand']

                    brand_user = User.objects.filter(
                        id=brand_login_user,
                        user_type='brand',
                        is_deleted=0)
                    if brand_user:
                        brand_id = brand_login_user
                        logo = json.dumps(
                            str(brand_user[0].user_logo)
                        )
                        user_slug = brand_user[0].slug
                        if logo:
                            user_logo = logo.replace('"', '')
            else:
                if superuser:
                    brand_users = User.objects.filter(
                        Q(user_type='brand', is_deleted=0)
                    ).order_by('id')[:1]
                else:
                    brand_users = User.objects.filter(
                        Q(created_by=user_id,
                            user_type='brand', is_deleted=0)
                    ).order_by('id')[:1]

                if brand_users:
                    brand_id = brand_users[0].id
                    user_slug = brand_users[0].slug
                    logo = json.dumps(str(brand_users[0].user_logo))
                    if logo:
                        user_logo = logo.replace('"', '')

        self.request.session['auth_brand_id'] = str(brand_id)
        self.request.session['auth_user_logo'] = user_logo
        self.request.session['auth_user_role'] = user_role
        self.request.session['auth_user_slug'] = user_slug
        self.request.session['auth_user_type'] = user_type
        self.request.session['is_superuser'] = superuser

        user = User.objects.get(id=user_id)
        user.last_login_json = dict(
            {'last_login_time': str(timezones()),
                'last_brand': brand_id})
        user.last_modified = timezones()
        user.ip_address = get_client_ip(self.request)
        user.save()

        login_log = User_Login_Log(
                        user_id=user_id, brand_id=brand_id,
                        ip_address=get_client_ip(self.request),
                        login_time=timezones(), createdAt=timezones())
        login_log.save()
        # ~ next_redirect = self.request.GET.get("next", "/")
        # ~ print('host', self.request.get_host())
        # ~ next_path = self.get_next_url()
        # next_path = '/'+user_slug+'/dashboard'
        next_path = '/dashboard'
        # ~ print('dsadas', next_path,
        # self.request.session['auth_enterprise_id'])
        return redirect(next_path)


class RegisterView(LoginRequiredMixin, PermissionRequiredMixin, View):
    form_class = UserRegisterForm
    template_name = 'users/add.html'
    model = User
    permission_required = "users.add_user"

    def get(self, request, *args, **kwargs):
        form = self.form_class(
            self.request.POST, created_by=request.session.get('_auth_user_id')
        )
        return render(self.request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):

        if self.request.method == "POST" and self.request.is_ajax():

            dict_session = session_dict(self.request)
            created_by = dict_session['_auth_user_id']
            auth_slug = dict_session['auth_user_slug']
            auth_type = dict_session['auth_user_type']
            
            form = self.form_class(
                request.POST, request.FILES, created_by=created_by
            )
            name = request.POST.get('name')
            role = request.POST.get('groups')

            if auth_type == 'brand':
                slug = auth_slug
            else:
                # ~ slug = unique_slug_generator(User, name)
                slug = 'admin'

            if form.is_valid():
                logo = False
                try:
                    if 'enterprise_logo' in request.FILES:
                        logo = request.FILES['enterprise_logo']
                    else:
                        logo = False
                except Exception:
                    logo = False

                user = form.save()
                if auth_type == 'admin':
                    user.user_type = 'brand'
                elif auth_type == 'brand':
                    user.user_type = 'sub-brand'

                group = Group.objects.get(id=role)
                if group:
                    # ~ user.groups.set(str(group.id))
                    group.user_set.add(user)
                    group_name = group.name
                    if group_name == 'Admin':
                        superuser = True
                        is_staff = False
                        is_admin = True
                    else:
                        superuser = False
                        is_staff = True
                        is_admin = False
                    user.created_by = created_by
                    user.staff = is_staff
                    user.slug = slug
                    user.admin = is_admin
                    user.enterprise_logo = logo
                    user.is_superuser = superuser
                    user.createdAt = timezones()
                    user.ip_address = get_client_ip(self.request)
                    user.last_modified = timezones()
                    user.save()

                    return JsonResponse({
                        "success": True,
                        'redirect_url': reverse('users:users', args=(auth_slug,)),
                        'msg': 'Record has been successfully submitted.'},
                        status=200)
            else:
                return JsonResponse({
                    "success": False,
                    'errors': form.errors.as_json()}, status=200)

            return JsonResponse({"success": False}, status=400)


class UserProfileUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, UpdateView
):

    model = User
    form_class = UserAdminChangeForm
    template_name = 'users/edit.html'
    permission_required = "users.change_user"
    user_idd = None

    def get(self, request, *args, **kwargs):
        encrypt_pk = self.kwargs['token']
        decrypt_pk = decrypt(encrypt_pk)

        dictionary = model_to_dict(
            User.objects.filter(pk=decrypt_pk).
            only('name', 'email', 'phone', 'user_logo', 'status')[0])

        groups = dictionary['groups']
        if groups:
            group_name = groups[0].__dict__['name']
            group = model_to_dict(
                Group.objects.filter(name=group_name).only('id')[0])
            group_dict = dict({'groups': group['id']})
        else:
            group_dict = {}
        userr = dict({"user": encrypt_pk})

        merge = {**dictionary, **userr, **group_dict}
        form = self.form_class(initial=merge,
                               created_by=request.session.get('_auth_user_id'))
        return render(self.request, self.template_name,
                      {"form": form, 'id': encrypt_pk,
                       "logo": dictionary['user_logo']})

    def post(self, request, *args, **kwargs):

        if self.request.method == "POST" and self.request.is_ajax():
            encrypt_pk = self.kwargs['token']
            decrypt_pk = decrypt(encrypt_pk)
            dict_session = session_dict(self.request)
            updated_by = dict_session['_auth_user_id']
            auth_slug = dict_session['auth_user_slug']

            form = self.form_class(self.request.POST, request.FILES,
                                   created_by=updated_by)
            name = request.POST.get('name')
            groupss = request.POST.get('groups')
            password = request.POST.get('password1')

            context = {'form': form}
            if form.is_valid():

                users = User.objects.get(id=decrypt_pk)
                group = Group.objects.get(id=groupss)
                if group:
                    # users.groups.clear()
                    # group.user_set.add(users)

                    # ~ users.groups.set(groupss)
                    group_name = group.name
                    if group_name == 'Admin':
                        superuser = True
                        is_staff = False
                        is_admin = True
                    else:
                        superuser = False
                        is_staff = True
                        is_admin = False
                    # ~ if group.name=='Enterprise':
                    try:
                        user_logo = request.FILES['user_logo']
                        users.user_logo = user_logo
                    except Exception:
                        users.user_logo = users.user_logo

                    users.staff = is_staff
                    users.admin = is_admin
                    users.slug = 'admin'
                    users.is_superuser = superuser
                    users.ip_address = get_client_ip(self.request)
                    users.last_modified = timezones()
                    users.modified_by = updated_by
                    users.name = name
                    if password:
                        users.set_password('{}'.format(password))
                    users.save()

                    return JsonResponse({
                        "success": True,
                        'redirect_url': reverse('users:users', args=(auth_slug,)),
                        'msg': 'User has been updated successfully.'},
                        status=200)
                else:
                    return JsonResponse({
                        "success": True,
                        'msg': 'Some error has been occurred.'}, status=200)
            else:
                return JsonResponse({
                    "success": False, 'errors': form.errors.as_json()},
                     status=200)


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = 'users/listing.html'
    model = User
    permission_required = "users.view_user"


class UserAjaxView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = 'users/ajax_listing.html'
    paginate_by = 10
    permission_required = "users.view_user"

    def get(self, request, *args, **kwargs):
        
        dict_session = session_dict(self.request)
        auth_role = dict_session['auth_user_role']
        auth_type = dict_session['auth_user_type']
        auth_brand_id = dict_session['auth_brand_id']
        created_by = dict_session['_auth_user_id']
        print('role', auth_role)
        page = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')

        if auth_brand_id and auth_type == 'brand':
            filter_enter = (Q(id=auth_brand_id) |
                            Q(created_by=auth_brand_id))
        elif auth_brand_id and auth_type == 'sub-brand':
            filter_enter = (Q(id=created_by))
        # ~ elif auth_brand_id and auth_type == 'admin':
            # ~ filter_enter = Q(id=auth_brand_id, created_by=created_by)
        else:
            filter_enter = Q(id__isnull=False)
        
        # ~ if (auth_role == None):
            
        user_obj = User.objects.filter(
            Q(email__icontains=filter_val) | Q(name__icontains=filter_val),
            Q(is_deleted=0), filter_enter
        ).order_by('-id').values(
            'id', 'name', 'email', 'phone', 'createdAt', 'groups__name')
        print(user_obj.query)
        total_count = user_obj.count()
        if total_count == 0:
            total_count = 'No'
        paginator = Paginator(user_obj, self.paginate_by)
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
                'html': html_form, 'pagination': html_pagi,
                'total_records': str(total_count)+' records found'})
        else:
            return super().get(request, *args, **kwargs)


class UserDelView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    permission_required = "users.delete_user"

    def get(self, request, *args, **kwargs):
        context = dict()
        if request.is_ajax():
            try:
                html_form = render_to_string(
                    'base/confirm_delete.html', context, request)
            except Exception:
                html_form = render_to_string(
                    'users/listing.html', context, request)

            return JsonResponse({'html': html_form})
        else:
            return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        dict_session = session_dict(self.request)
        auth_slug = dict_session['auth_user_slug']

        if self.request.is_ajax():
            try:
                idd = self.request.POST.getlist('ids[]')
                indexes = [int(decrypt(i)) for i in idd]
                # ~ print('idne', indexes)
                obj = User.objects.filter(
                    Q(is_deleted=0, enterprise_groups__isnull=True),
                    Q(id__in=indexes))

                if obj:
                    User.objects.filter(
                        Q(is_deleted=0, id__in=indexes)
                        ).update(is_deleted=1)
                    return JsonResponse({
                        "success": True,
                        'msg': 'User has been successfully deleted.'},
                         status=200)
                else:
                    return JsonResponse({
                        "success": False,
                        'msg': 'User is already associated with group, first \
                        of all delete them.'},
                         status=200)
            except Exception:
                return JsonResponse({
                    "success": False,
                    'msg': 'Some error has been occurred, please try again.'},
                     status=200)
        else:
            return self.delete(*args, **kwargs)


class ChangePasswordView(LoginRequiredMixin, UpdateView):
    form_class = ChangePasswordForm
    template_name = "users/change_password.html"
    initial = {'key': 'value'}

    def get(self, request, *args, **kwargs):
        auth_user_role = request.session.get('auth_user_role')

        form = self.form_class(initial=self.initial, user_role=auth_user_role)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        auth_user_role = request.session.get('auth_user_role')

        form = self.form_class(request.POST, user_role=auth_user_role)
        old_pass = request.POST.get('old_password')
        new_password = request.POST.get("new_password")

        user = User.objects.get(id=request.session.get('_auth_user_id'))
        if auth_user_role == 'None':
            old_pass = '111111111111111111111111111111\
            1111111111111111111111111111111'

        else:
            if old_pass:
                # ~ user = User.objects.get(email = request.user)
                if not user.check_password('{}'.format(old_pass)):
                    form.add_error('old_password',
                                   'The old password does not match.')
        if form.is_valid():
            user.set_password('{}'.format(new_password))
            user.save()
            update_session_auth_hash(request, user)
            messages.success(self.request,
                             'Password has been changed successfully!')
            return HttpResponseRedirect(
                reverse('dashboard'
                        ))

        return render(request, self.template_name, {'form': form})


class ChangeEnterprise(LoginRequiredMixin, UpdateView):
    model = User

    def get(self, request, *args, **kwargs):
        session_val = self.request.session.items()
        user_id = dict(session_val)['_auth_user_id']
        brand_id = request.GET.get('enterp')
        if brand_id == '0':
            brand_user = User.objects.filter(
                created_by=brand_id, is_deleted=0)
        else:
            brand_user = User.objects.filter(
                id=brand_id, user_type='brand', is_deleted=0)
        if brand_user:
            logo = json.dumps(str(brand_user[0].user_logo))
            slug = brand_user[0].slug
            if logo:
                self.request.session['auth_user_logo'] = logo.replace(
                    '"', '')

            # ~ self.request.session['auth_brand_id'] = str(brand_id)
            self.request.session['auth_brand_id'] = int(brand_id)
            self.request.session['auth_user_slug'] = slug
            
            # update last login json
            user = User.objects.get(id=user_id)
            last_login_json = user.last_login_json
            if last_login_json:
                last_login_json.update({'last_brand': brand_id})
                user.last_login_json = last_login_json
                user.save()

            # update user log
            user_log = User_Login_Log.objects.filter(user_id=user_id).order_by(
                '-id')[:1]
            if user_log:
                User_Login_Log.objects.filter(id=user_log[0].id).update(
                    brand_id=brand_id)

            return JsonResponse({
                'success': True,
                # ~ 'redirect_url': '/'+slug+'/dashboard'},
                'redirect_url': '/dashboard'},
                 status=200)
        else:
            return JsonResponse({'success': False}, status=200)

