import os
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, FormView, UpdateView, ListView, DeleteView
from django.shortcuts import render,redirect, get_object_or_404
from django.core.paginator import Paginator
from django.template.loader import render_to_string, get_template
from django.http import JsonResponse
from django.db.models import Q, Count
from django.conf import settings
from .ajax_views import *
from .forms import *
from americana.utils import session_dict, get_client_ip, model_to_dict, timezones
from americana.files import file_upload
from americana.encryption import encrypt, decrypt
from .models import Posts, PostActivities, PostsReaction, PostComments
from postcategory.models import PostCategory

POST_IMAGE_LOCATION = '/root/americana/Americana/americana/static_cdn/upload_media/post/image/'
POST_IMAGE_UPLOAD_PATH = '/media/post/image/'
POST_FILE_LOCATION = '/root/americana/Americana/americana/static_cdn/upload_media/post/file/'
POST_FILE_UPLOAD_PATH = '/media/post/file/'

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model               = Posts
    template_name       = 'post/listing.html'
    permission_required = 'post.delete_posts'
    
    def get(self, request, *args, **kwargs):
        
        context = dict()
        if request.is_ajax():
            try:
                html_form = render_to_string(
                    'base/confirm_delete.html', context, request)
            except Exception:
                html_form = render_to_string(
                    'post/listing.html', context, request)
            return JsonResponse({'html': html_form})
        else:
            return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        dict_session = session_dict(self.request)
        updated_by = dict_session['_auth_user_id']
        try :
            ids = request.POST.getlist('ids[]')
            indexes = [int(decrypt(i)) for i in ids]
            for post_id in indexes:
                post_obj = Posts.objects.filter(Q(id=post_id))
                if post_obj:
                    PostActivities.objects.filter(post_id=post_id).delete()
                    PostComments.objects.filter(post_id=post_id).delete()
                    PostsReaction.objects.filter(post_id=post_id).delete()
                    exist_files = post_obj[0].post_file
                    exist_images = post_obj[0].post_image
                    if exist_files:
                        for image in exist_files:
                            exist_url = image['fileURL']
                            existing_file = exist_url.replace(settings.BASE_URL+'/media/post/file', '')
                            if os.path.exists(POST_FILE_LOCATION+'/'+existing_file):
                                os.remove(POST_FILE_LOCATION+'/'+existing_file)
                    if exist_images:
                        for image in exist_images:
                            exist_url = image['fileURL']
                            existing_file = exist_url.replace(settings.BASE_URL+'/media/post/image', '')
                            if os.path.exists(POST_IMAGE_LOCATION+'/'+existing_file):
                                os.remove(POST_IMAGE_LOCATION+'/'+existing_file)
                    post_obj.delete()
            return JsonResponse({"success": True, 'msg': 'Post has been successfully deleted.'}, status=200)
            
        except Exception:
            return JsonResponse({"success": False, 'msg': 'Some error has been occurred, please try again.'}, status=200)
            

class PostCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    
    permission_required = "post.add_posts"
    form_class          = PostsAdminCreationForm
    model               = Posts
    template_name       = 'post/add.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST)
        return render(self.request, self.template_name, {"form": form})
    
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            dict_session = session_dict(self.request)
            created_by = dict_session['_auth_user_id']
            ip_address = get_client_ip(self.request)
            # ~ auth_slug     = dict_session['auth_user_slug']
            brand_id = dict_session['auth_brand_id']
            form = self.form_class(self.request.POST, request.FILES)
            
            file_type = self.request.POST.get('file_type')
            if file_type == 'image' and 'upldFile' in request.FILES:
                post_image = request.FILES['upldFile']
                sample=request.FILES.getlist('upldFile')
            else:
                post_image = False
                
            if (file_type == 'video' or file_type == 'file') and 'upldFile' in request.FILES:
                post_file = request.FILES['upldFile']
                sample=request.FILES.getlist('upldFile')
            else:
                post_file = False
            
            imagess = list()            
            filess = list()
            # ~ post_image = False
            # ~ post_file = False
            if post_image:
                for i in sample:
                    image_json = dict()
                    upload_image = file_upload(i, POST_IMAGE_LOCATION, POST_IMAGE_UPLOAD_PATH) 
                    if upload_image==False:
                        return JsonResponse({"success" : False, 'msg' : 'Some error has been occurred for upload he post image, please try again.'}, status=200)
                    else:
                        image_json['fileURL']  = settings.BASE_URL+upload_image['upload_url']
                        image_json['fileHash'] = upload_image['hash']
                        image_json['fileSize'] = upload_image['size']
                    imagess.append(image_json)

            if post_file:
                for i in sample:
                    file_json = dict()
                    upload_file = file_upload(i, POST_FILE_LOCATION, POST_FILE_UPLOAD_PATH) 
                    if upload_file==False:
                        return JsonResponse({"success" : False, 'msg' : 'Some error has been occurred for upload he post image, please try again.'}, status=200)
                    else:
                        file_json['fileURL']  = settings.BASE_URL+upload_file['upload_url']
                        file_json['fileHash'] = upload_file['hash']
                        file_json['fileSize'] = upload_file['size']
                    filess.append(file_json)
                    
            english_title = self.request.POST.get('english_title')
            arabic_title = self.request.POST.get('arabic_title')
            english_description = self.request.POST.get('english_description')
            arabic_description = self.request.POST.get('arabic_description')
            
            post_type = self.request.POST.get('post_type')
            user_id = self.request.POST.get('user_id')
            post_category = self.request.POST.get('post_category')
            post_image = imagess
            post_file = filess
            print('postt', post_category)
            approve_status = self.request.POST.get('approve_status')
            # ~ post_language = self.request.POST.get('post_language')
            
            title = dict()
            desc = dict()
            title['english'] = english_title 
            title['arabic'] = arabic_title 
            desc['english'] = english_description 
            desc['arabic'] = arabic_description
            
            if form.is_valid():
                post_obj = Posts(
                                title = title,
                                description = desc,
                                post_type = 'post',
                                post_category = PostCategory.objects.filter(id=post_category)[0],
                                post_image = post_image,
                                post_file = post_file,
                                file_type = file_type,
                                approve_status = approve_status,
                                # ~ post_language = post_language,
                                createdAt = timezones(),
                                created_by = created_by,
                                post_author = 'admin',
                                brand_id = brand_id,
                                ip_address = ip_address
                            )
                post_obj.save()
                if post_obj.id:
                    return JsonResponse({"success" : True, 'redirect_url' : reverse('post:post'), 'msg' : 'Post has been created successfully.'}, status=200)
                else:
                    return JsonResponse({"success" : False, 'msg' : 'Some error has been occurred.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success":False}, status=400)


class PostFileView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    
    permission_required = "post.add_posts"
    form_class          = PostsAdminCreationForm
    model               = Posts
    template_name       = 'post/add-file.html'
    # ~ if request.method == 'POST':  
        # ~ file = request.FILES['file'].read()
        # ~ fileName= request.POST['filename']
        # ~ existingPath = request.POST['existingPath']
        # ~ end = request.POST['end']
        # ~ nextSlice = request.POST['nextSlice']

        # ~ if file=="" or fileName=="" or existingPath=="" or end=="" or nextSlice=="":
            # ~ res = JsonResponse({'data':'Invalid Request'})
            # ~ return res
        # ~ else:
            # ~ if existingPath == 'null':
                # ~ path = 'media/' + fileName
                # ~ with open(path, 'wb+') as destination: 
                    # ~ destination.write(file)
                # ~ FileFolder = File()
                # ~ FileFolder.existingPath = fileName
                # ~ FileFolder.eof = end
                # ~ FileFolder.name = fileName
                # ~ FileFolder.save()
                # ~ if int(end):
                    # ~ res = JsonResponse({'data':'Uploaded Successfully','existingPath': fileName})
                # ~ else:
                    # ~ res = JsonResponse({'existingPath': fileName})
                # ~ return res
            # ~ else:
                # ~ path = 'media/' + existingPath
                # ~ model_id = File.objects.get(existingPath=existingPath)
                # ~ if model_id.name == fileName:
                    # ~ if not model_id.eof:
                        # ~ with open(path, 'ab+') as destination: 
                            # ~ destination.write(file)
                        # ~ if int(end):
                            # ~ model_id.eof = int(end)
                            # ~ model_id.save()
                            # ~ res = JsonResponse({'data':'Uploaded Successfully','existingPath':model_id.existingPath})
                        # ~ else:
                            # ~ res = JsonResponse({'existingPath':model_id.existingPath})    
                        # ~ return res
                    # ~ else:
                        # ~ res = JsonResponse({'data':'EOF found. Invalid request'})
                        # ~ return res
                # ~ else:
                    # ~ res = JsonResponse({'data':'No such file exists in the existingPath'})
                    # ~ return res
    # ~ return render(request, 'post/add-file.html')


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):    
    
    permission_required = "post.change_posts"  
    model               = Posts
    form_class          = PostUpdateForm
    template_name       = 'post/edit.html'
    initial             = {'key' : 'value'}
    
    def get(self, request, *args, **kwargs):
        encrypt_pk = self.kwargs['token']
        decrypt_pk = decrypt(encrypt_pk) 
        
        instance = get_object_or_404(Posts, pk=decrypt_pk)
        dictionary = model_to_dict(Posts.objects.filter(pk=decrypt_pk).only('title', 'post_category', 'description', 'approve_status')[0])
        if 'english' in dictionary['title']:
            dictionary['english_title'] = dictionary['title']['english']
        else:
            dictionary['english_title'] = ''
        if 'arabic' in dictionary['title']:
            dictionary['arabic_title'] = dictionary['title']['arabic']
        else:
            dictionary['arabic_title'] = ''
        if 'arabic' in dictionary['description']:
            dictionary['arabic_description'] = dictionary['description']['arabic']
        else:
            dictionary['arabic_description'] = ''
        if 'english' in dictionary['description']:
            dictionary['english_description'] = dictionary['description']['english']
        else:
            dictionary['english_description'] = ''
        form = self.form_class(initial=dictionary, instance=instance)
       
        return render(self.request, self.template_name, {"form": form, 'id': encrypt_pk})
        
    def post(self, request, *args, **kwargs):
        
        if self.request.method == "POST" and self.request.is_ajax():
            encrypt_pk   = self.kwargs['token']
            decrypt_pk   = decrypt(encrypt_pk) 
            instance     = get_object_or_404(Posts, id=decrypt_pk, is_deleted=False)
            dict_session = session_dict(self.request)
            updated_by   = dict_session['_auth_user_id']
            auth_slug    = dict_session['auth_user_slug']
            form  = self.form_class(self.request.POST, request.FILES, instance=instance)
            # ~ title = request.POST.get('title')
            # ~ description = request.POST.get('description')
            # ~ post_type = self.request.POST.get('post_type')
            # ~ user = self.request.POST.get('user')
            post_category = self.request.POST.get('post_category')
            # ~ post_image = self.request.POST.get('post_image')
            # ~ post_file = self.request.POST.get('post_file')
            # ~ file_type = self.request.POST.get('file_type')
            
            approve_status = self.request.POST.get('approve_status')
            
            title = dict()
            desc = dict()
            title['english'] = self.request.POST.get('english_title')
            title['arabic'] = self.request.POST.get('arabic_title')
            desc['english'] = self.request.POST.get('english_description')
            desc['arabic'] = self.request.POST.get('arabic_description')
            
            if form.is_valid():
                posts = Posts.objects.get(id=decrypt_pk, is_deleted=False)
               
                posts.title = title
                posts.description = desc
                # ~ posts.post_type = post_type
                # ~ posts.user_id = user
                posts.post_category_id = int(post_category)
                # ~ if post_image:
                    # ~ posts.post_image = post_image
                # ~ if post_file:
                    # ~ posts.post_file = post_file
                # ~ posts.file_type = file_type
                # ~ posts.taggedusers = taggedusers
                # ~ posts.like_count = like_count
                # ~ posts.comment_count = comment_count
                posts.approve_status = approve_status
                # ~ posts.status = status
                posts.updated_by = updated_by
                posts.ip_address = get_client_ip(self.request)
                # ~ posts.post_language = post_language
                posts.updatedAt  = timezones()
              
                posts.save()
                return JsonResponse({"success" : True, 'redirect_url' : reverse('post:post'), 'msg' : 'Post has been updated successfully.'}, status=200)
            else:
               return JsonResponse({"success" : False, 'errors' : form.errors.as_json()}, status=200)
                
            return JsonResponse({"success" : False}, status=400)
    
    
class PostListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "post.view_posts"
    template_name       = 'post/listing.html'
    model               = Posts


class PostAjaxView(ListView):
    model               =  Posts
    permission_required = "post.view_posts"
    template_name       = 'post/ajax_listing.html'
    paginate_by         = 10
    
    def get(self, request, *args, **kwargs):
        
        dict_session = session_dict(self.request)
        auth_brand_id = dict_session['auth_brand_id']
        
        page = request.GET.get('page', 1)
        filter_val = request.GET.get('keywords', '')
        
        if auth_brand_id:
            brand_filter = Q(is_deleted=False, brand_id=auth_brand_id, post_type='post')
        else:
            brand_filter = Q(is_deleted=False, post_type='post')
            
        mod_obj = Posts.objects.filter((Q(title__icontains=filter_val) | Q(description__icontains=filter_val) | Q(post_type__icontains=filter_val) | Q(post_category__name__icontains=filter_val) | Q(user__employee_code__icontains=filter_val)),
            brand_filter).values('id', 'title__english', 'title__arabic', 'description','post_type','user_id__employee_code','post_category__name','post_language' ,'post_image', 'post_file', 'file_type', 'like_count','comment_count','approve_status','status', 'createdAt').order_by('-id')
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
