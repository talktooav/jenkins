import random
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.generics import GenericAPIView
from django.views.generic import UpdateView
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.conf import settings

from quiz.forms import QuizResultAdminCreationForm
import os
from googletrans import Translator

from quiz.models import Quizes,QuizQuestions,QuizResult
from jobusers.models import JobUsers, Job_User_Points_Log
from post.models import Posts, PostActivities, PostsReaction,PostComments
from americanaStore.models import Products,JobUserStore
from rewards.models import StarOfTheMonth,Points
from pushNotification.models import Notification
from moderation.models import Moderation
from postcategory.models import PostCategory

from account.serializers import CustomUserSerializer, PostActivitiesSerializer, WishUserBirthdaySerializer, PostSerializer, NotificationSerializer, QuizResultSerializer,PostCommentSerializer
from account.backends import TokenAuthentication


from americana.utils import session_dict, get_client_ip, model_to_dict, timezones
from datetime import timedelta

from PIL import Image
import io
import jwt
import base64
from django.core.files.base import ContentFile
import json
from quiz.forms import QuizResultAdminCreationForm
from americana.utils import  send_push_notification
from americana.files import file_upload


POST_IMAGE_LOCATION = '/root/americana/Americana/americana/static_cdn/upload_media/post/image/'
POST_IMAGE_UPLOAD_PATH = '/media/post/image/'
POST_FILE_LOCATION = '/root/americana/Americana/americana/static_cdn/upload_media/post/file/'
POST_FILE_UPLOAD_PATH = '/media/post/file/'



class BirthdayPost(GenericAPIView):
    authentication_classes = (TokenAuthentication,) 

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('employee_id', False)
        
        k=JobUsers.objects.filter(employee_code=user_id).values('id','language','brand_id')
        brand_id=k[0].get('brand_id')
        language=k[0].get('language')
        post_type='birthday'
        posts=Posts.objects.filter(post_type='birthday').values('id', 'user_id__employee_name','user_id__userProfileImage', 'user_id__employee_code', 'post_type', 'title', 'description', 'post_file', 'post_category__name','createdAt').order_by('-createdAt')
        for i in posts:
            title=i.get('title')
            description=i.get('description')
            titl=''
            desc=''
            if language: # 0 = english and 1 = arabic
                
                titl=title.get('arabic')
                if titl=='':
                    titl=title.get('english')
                
                desc=description.get('arabic')
                if desc=='':
                    desc=description.get('english')
            else:
                titl=title.get('english')
                desc=description.get('english')
            i['title']=titl
            i['description']=desc

        return Response({'status' : True,'count':len(posts),'result':posts})


class StoreProducts(GenericAPIView):
    authentication_classes = (TokenAuthentication,) 

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('employee_id', False)
        user=JobUsers.objects.filter(employee_code=user_id).values('id','user_point','employee_code','employee_name','brand_id','language')
        user_point=user[0].get('user_point')
        language=user[0].get('language')
        products=list(Products.objects.filter(is_deleted=False).values('id','name','description','price','product_image'))
        

        for item in products:
            if language:
                trans=Translator()
                name=item.get('name')
                name1=trans.translate(name,src='en',dest='ar')
                item["name"]=str(name1.text)
                # print(item1["user_id__employee_name"],"===============================================",name1.text)
                description=item.get('description')
                description=trans.translate(description,src='en',dest='ar')
                item["description"]=str(description.text)
        
        return Response({'status' : True,'count':len(products),'result':products,'user_point':user_point})

class RedeemPoints(GenericAPIView):
    authentication_classes = (TokenAuthentication,) 

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('employee_id', False)
        product_id=request.data.get('product_id', False)

        user=JobUsers.objects.filter(employee_code=user_id).values('id','user_point','employee_code','employee_name','brand_id')
        product=Products.objects.filter(id=product_id,is_deleted=False).values('id','price')
        user_point=user[0].get('user_point')
        price=product[0].get('price')
        
        if price>user_point:
            return Response({'status' : False,'result':"You don't have enough points to redeem it.",'product_id':product_id })    
        else:
            # new_user_point=user_point-price
            # JobUsers.objects.filter(employee_code=user_id).update(user_point=new_user_point)
            userstore=JobUserStore(product_id=product[0].get('id'),user_id=user[0].get('id'),boughtAt=timezones(),brand_id=user[0].get('brand_id'),ip_address = get_client_ip(self.request))
            userstore.save()
            return Response({'status' : True,'result':"Thank you! Your request have been submitted. The HR team will get in touch with you.",'product_id':product_id })
        
        return Response({'status' : True,'count':len(products),'result':products})

class Country(APIView):
    def get(self, request, *args, **kwargs):

        country_name=['UAE','Egypt','Saudi Arabia','Kuwait','Bahrain','Jordan','Morocco','Lebanon','Iraq']
        country_flag=["http://52.66.228.107:8080/media/country/United_Arab_Emirates-100.jpg","http://52.66.228.107:8080/media/country/Egypt-100.jpg","http://52.66.228.107:8080/media/country/Saudi_Arabia-100.jpg","http://52.66.228.107:8080/media/country/Kuwait-100.jpg","http://52.66.228.107:8080/media/country/Bahrain-100.jpg","http://52.66.228.107:8080/media/country/Jordan-100.jpg","http://52.66.228.107:8080/media/country/Morocco-100.jpg","http://52.66.228.107:8080/media/country/Lebanon-100.jpg","http://52.66.228.107:8080/media/country/Iraq-100.jpg"]
        sample=[{'country':country_name[0],
                'flag':country_flag[0]
                },{'country':country_name[1],
                'flag':country_flag[1]
                },{'country':country_name[2],
                'flag':country_flag[2]
                },{'country':country_name[3],
                'flag':country_flag[3]
                },{'country':country_name[4],
                'flag':country_flag[4]
                },{'country':country_name[5],
                'flag':country_flag[5]
                },{'country':country_name[6],
                'flag':country_flag[6]
                },{'country':country_name[7],
                'flag':country_flag[7]
                },{'country':country_name[8],
                'flag':country_flag[8]
                }]
        print(sample)
        if(request.method=="GET"):

            return Response(sample)

class PollResult(GenericAPIView):
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
            user_id = request.data.get('employee_id', False)
            post_id = request.data.get('post_id', False)
            user_id=JobUsers.objects.filter(employee_code=user_id).values('language')
            poll = Posts.objects.extra(select={'created_user' : "SELECT name FROM amrc_users WHERE amrc_users.id=amrc_posts.created_by",'userProfileImage' : "SELECT user_logo FROM amrc_users WHERE amrc_users.id=amrc_posts.created_by"}).filter(id=post_id).filter(post_type ='poll',is_deleted=False,user__isnull=True).values('id', 'created_user','userProfileImage' ,'post_type', 'post_category__name','title', 'description', 'createdAt','userProfileImage','reactions').order_by('-createdAt')
            for i in poll:
                i["userProfileImage"]=settings.BASE_URL+"/media/"+i.get("userProfileImage")

            # poll=Posts.objects.filter(id=post_id).values('id','reactions','')
            data = poll[0]
            d1 = {"reactions": json.loads(poll[0]['reactions'])}
            print(json.loads(poll[0]['reactions']))
            data.update(d1)
            result=list()
            sample=dict()
            total=len(PostActivities.objects.filter(option_name='poll_feedback',post_id=post_id).values('option_val'))
            number=0
            for i in d1["reactions"]:
                # print(i)
                number+=1
                
                answer=i.get('label')
                value=len(PostActivities.objects.filter(option_name='poll_feedback',post_id=post_id,option_val=answer).values('option_val'))
                percent=(value/total)*100
                sample={"option_val":answer}
                print(result)    
                sample={"percent":str(round(percent))+" %", str(number):round(percent)/100 ,'option_val':answer}

                result.append(sample)

            
            # for i in result:
            return Response({'status' : True, 'result' : result,'title':poll[0].get("title"),'userProfileImage':poll[0].get("userProfileImage"),'created_user':poll[0].get("created_user")})

class PendingPost(APIView):
    authentication_classes = (TokenAuthentication,) 

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('employee_id', False)
        
        k=JobUsers.objects.filter(employee_code=user_id).values('id','language')
        user_id=k[0].get('id')
        language=k[0].get('language')
        posts=list(Posts.objects.filter(approve_status=0,user_id=user_id,post_language=language,is_deleted=False).values('id', 'user_id__employee_name','user_id__userProfileImage', 'user_id__employee_code', 'post_type', 'title', 'description', 'post_file', 'post_category__name', 'post_image', 'file_type', 'approve_status','createdAt').order_by('-createdAt'))
        for i in posts:
            title=i.get('title')
            description=i.get('description')
            titl=''
            desc=''
            if language: # 0 = english and 1 = arabic
                
                titl=title.get('arabic')
                if titl=='':
                    titl=title.get('english')
                
                desc=description.get('arabic')
                if desc=='':
                    desc=description.get('english')
            else:
                titl=title.get('english')
                desc=description.get('english')
            i['title']=titl
            i['description']=desc

        return Response({'status' : True,'count':len(posts),'result':posts})


class postList(GenericAPIView):
    '''
    Create Post API
    '''
    authentication_classes = (TokenAuthentication,) 
    serializer_class    = PostSerializer
    pagination_class = PageNumberPagination
    def post(self, request):

        if(request.method=="POST"):
            userId      = request.data.get('employee_id', False)
            category_id = request.data.get('category_id', False)

            post_ids = []
            k=JobUsers.objects.filter(employee_code=userId).values('language','brand_id')
            brand_id=k[0].get('brand_id')
            language=k[0].get('language')
            
            queryset1 = list(Posts.objects.extra(select={'user_id__employee_name' : "SELECT name FROM amrc_users WHERE amrc_users.id=amrc_posts.created_by",'user_id__userProfileImage' : "SELECT user_logo FROM amrc_users WHERE amrc_users.id=amrc_posts.created_by"}).exclude(is_deleted=True).filter(user__isnull=True,approve_status=1,brand_id=brand_id).values('id', 'user_id__employee_name','user_id__userProfileImage', 'user_id__employee_code', 'post_type', 'title', 'description', 'post_file','post_category__name','post_image', 'file_type','approve_status','like_count','shock_count','smile_count','heart_count','total_count','created_by' ,'comment_count', 'createdAt').order_by('-id') )
            for i in queryset1:
                title=i.get('title')
                description=i.get('description')
                titl=''
                desc=''
                if language: # 0 = english and 1 = arabic
                    
                    titl=title.get('arabic')
                    if titl=='':
                        titl=title.get('english')
                    
                    desc=description.get('arabic')
                    if desc=='':
                        desc=description.get('english')
                else:
                    titl=title.get('english')
                    desc=description.get('english')
                i['title']=titl
                i['description']=desc

            queryset2 = list(Posts.objects.exclude(user__isnull=True).filter(approve_status=1,brand_id=brand_id).values('id', 'user_id__employee_name','user_id__userProfileImage', 'user_id__employee_code', 'post_type', 'title', 'description', 'post_file','post_category__name', 'post_image', 'file_type', 'approve_status','like_count','shock_count','smile_count','heart_count','total_count' ,'comment_count', 'createdAt').order_by('-id') )
            for i in queryset2:
                title=i.get('title')
                description=i.get('description')
                titl=title.get('english')
                desc=description.get('english')
                i['title']=titl
                i['description']=desc
            queryset3=queryset2+queryset1
            queryset3=sorted(queryset3, key = lambda item: item['createdAt'],reverse=True)

            for item1 in queryset3:
                post_id=item1.get('id')
                comments=list(PostComments.objects.filter(post_id=post_id).values('user_id__employee_name','user_id__userProfileImage','comment').order_by('-createdAt'))
                
                if len(comments)<3:
                    item1.update({"comments":comments})
                else:
                    comments=list(PostComments.objects.filter(post_id=post_id).values('user_id__employee_name','user_id__userProfileImage','comment').order_by('-createdAt'))[0:2]    
                    item1.update({"comments":comments})

                j=Posts.objects.filter(id=item1.get('id')).values('like_count','shock_count','smile_count','heart_count','total_count')
                shock_count = j[0].get('shock_count')
                smile_count = j[0].get('smile_count')
                heart_count = j[0].get('heart_count')
                like_count = j[0].get('like_count')
                total_count=shock_count+smile_count+heart_count+like_count
                Posts.objects.filter(id = item1.get('id')).update(total_count=total_count)

            page = self.paginate_queryset(queryset3)
            
            # update user time to track active Inactive
            JobUsers.objects.filter(id=userId).update(logged_in_time = timezones())
            
            if page is not None:
                return self.get_paginated_response(page)

            serializer = self.get_serializer(queryset3, many=True)
            return Response(queryset3)

class CreatePost(APIView):
    
    authentication_classes = (TokenAuthentication,) 
    parser_classes = (MultiPartParser, FormParser, FileUploadParser,)

    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
            
            user_id = request.data.get('employee_id', False)
            is_entity = request.data.get('is_entity', False)
            title = request.data.get('title', False)
            description = request.data.get('description', False)
            post_category_id = request.data.get('post_category_id', False)

            if 'post_image' in request.FILES:
                post_image = request.FILES['post_image']
                sample=request.FILES.getlist('post_image')
            else:
                post_image = False
                
            if 'post_file' in request.FILES:
                post_file = request.FILES['post_file']
                sample=request.FILES.getlist('post_file')
            else:
                post_file = False

            old = JobUsers.objects.filter(employee_code = user_id)
            user=old.values('id','employee_code','language','user_point','brand_id','employee_name','job_role__name','userProfileImage')
            user_id=user[0].get('id')
            brand_id=user[0].get('brand_id')
            language=user[0].get('language')
            user_point=user[0].get('user_point')
            imagess=list()            
            filess=list()

            if old.exists():

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
                
                request.data._mutable = True
                request.data['post_type'] = 'post'
                
                if 'post_image' in request.data:
                    request.data.pop('post_image')
                if 'post_file' in request.data:
                    request.data.pop('post_file')
                                
                if(is_entity == '1'):
                    entitydata = JobUsers.objects.filter(id = user_id).values('entity_id').first()
                    entity_id = entitydata['entity_id'] if entitydata['entity_id'] else 0
                else:
                    entity_id = 0

                post_status = 0
                if (user[0]['job_role__name'] =='RGM') | (user[0]['job_role__name'] =='Operations Manager') | (user[0]['job_role__name'] =='Field Training Manager') | (user[0]['job_role__name'] =='Human Resources Manager') | (user[0]['job_role__name'] =='Marketing Associate') | (user[0]['job_role__name'] =='Marketing Manager') | (user[0]['job_role__name'] =='Chief Operations Officer') | (user[0]['job_role__name'] =='Director Ops Excellence & CX') | (user[0]['job_role__name'] =='Senior Operations Excellence Manager') | (user[0]['job_role__name'] =='HR Director') | (user[0]['job_role__name'] =='Human Resources Senior Manager') | (user[0]['job_role__name'] =='Human Resources Associate') | (user[0]['job_role__name'] =='Training Associate') | (user[0]['job_role__name'] =='Marketing Director') | (user[0]['job_role__name'] =='Marketing Senior associate') | (user[0]['job_role__name'] =='Area Operations Director') | (user[0]['job_role__name'] =='Operations Manager'):
                    post_status = 1

                if title!=False:
                    title={"arabic":"","english":title}
                else:
                    title={"arabic":"","english":""}

                desc ={"arabic":"","english":description}
                if 'description' in request.data:
                    request.data.pop('description')

                # description = json.dumps(desc)

                post = PostSerializer(data=request.data)
                if post.is_valid(raise_exception=True):
                    post.save(
                            post_image = imagess,
                            post_file = filess,
                            createdAt = timezones(),
                            is_entity = entity_id,
                            title=title,
                            description=desc,
                            post_language=language,
                            ip_address = get_client_ip(self.request),
                            brand_id=brand_id,
                            approve_status = post_status,
                            user_id = user_id,
                            status = True
                    )

                # print(post.data,"---------------------------------------------------")
                # post.save()

                # post={"post_image" : imagess,
                #         "post_file" : filess,
                #         "createdAt" : timezones(),
                #         "title":title,
                #         "description":description,
                #         "post_language":language,
                #         "ip_address" : get_client_ip(self.request),
                #         "approve_status" : post_status,
                #         "user_id" : user_id,
                #         "user_id__employee_code":user[0].get("employee_code"),
                #         "user_id__employee_code":user[0].get("userProfileImage"),
                #         "status" = True}
                
                # Adding points on post creation
                points=get_points(user_id,'post','Create post')
                user_point+=points
                JobUsers.objects.filter(id=user_id).update(user_point=user_point)
                # End

                # SEND PUSH NOTIFICATION TO TAGGED USER
                # for tag_user_id in tagged_users:
                #     tag_device_id = get_device_id(tag_user_id)
                #     payload = {"to": tag_device_id,"notification": {"body": "The first message from the React Native and Firebase","title": "you are tagged","content_available": True,"priority": "high"},"data": {"post_id": post_id}}
                #     send_push_notification(payload)
                # END
                post=post.data
                post['title']=post['title'].get("english")
                post['description']=post['description'].get("english")
                # Adding notification
                if post_status:
                    title = user[0].get('employee_name')
                    sub_title = "added new post"

                    data = {"type":"post","link":""}
                    import json
                    json_data= json.dumps(data)
                    # print(type(json_data))
                    add_notification('normal', user_id,'','','global',title,sub_title,json_data)
                # END

                return Response({
                'status' : True,
                'detail' : 'Post has been created successfully',
                'data'   : post
                })

            else:
                return Response({
                    'status' : False,
                    'detail' : 'User not exist'
                    })
        else:
            return Response("", status=404)


class UpdatePost(GenericAPIView):
    '''
    Update Post API
    '''
    authentication_classes = (TokenAuthentication,) 
    def post(self,request,*args,**kwargs):
        if(request.method=="POST"):
            post_id = request.data.get('post_id', False)
            user_id = request.data.get('employee_id', False)
            description = request.data.get('description',False)
            file_type = request.data.get('file_type',False)
            sample=request.FILES.getlist('post_file')
            if 'post_image' in request.FILES:
                post_image = request.FILES['post_image']
                sample=request.FILES.getlist('post_image')
            else:
                post_image = False
                
            if 'post_file' in request.FILES:
                post_file = request.FILES['post_file']
                sample=request.FILES.getlist('post_file')
            else:
                post_file = False

            old = JobUsers.objects.filter(id__iexact = user_id)
            imagess=list()            
            filess=list()
            # image_json = dict()
            
            if old.exists():

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

                # print(imagess,'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
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
                
                request.data._mutable = True
                request.data['post_type'] = 'post'
                
                if 'post_image' in request.data:
                    request.data.pop('post_image')
                if 'post_file' in request.data:
                    request.data.pop('post_file')

                if title!=False:
                    title={"arabic":"","english":title}
                else:
                    title={"arabic":"","english":""}

                desc ={"arabic":"","english":description}
                if 'description' in request.data:
                    request.data.pop('description')

            if post_id and user_id:
                old = Posts.objects.filter(id = post_id).update(description=desc,post_image=imagess,post_file=filess,updatedAt=timezones(),file_type=file_type)
                if old:
                    old=Posts.objects.filter(id = post_id).values('id', 'title', 'description','post_type','user_id__employee_name','user_id__userProfileImage', 'user_id__employee_code','post_category__name','post_image', 'post_file', 'like_count','shock_count','smile_count','heart_count','comment_count','approve_status','updatedAt')
                    return Response({'status' : True, 'Updated_post' : old[0]})
                else:
                    return Response({'status' : False, 'detail' : 'Post id wrong'})



class PostAddPostLike(APIView):
    '''
    When user React or like any post
    '''
    authentication_classes = (TokenAuthentication,) 

    def post(self, request, *args, **kwargs):
        # employee_id = request.query_params.get('employee_id')
        user_id = request.data.get('employee_id', False)
        post_id = request.data.get('post_id', False)
        reaction = request.data.get('reaction', False)

        if user_id and post_id and reaction:
            User=JobUsers.objects.filter(employee_code = user_id).values('id')
            user_id=User[0].get('id')
            user_data = JobUsers.objects.filter(id = user_id).values('id', 'job_role__name', 'employee_code','employee_name','gender','market','job_role','date_of_birth', 'userProfileImage','user_point')
            
            if user_data.exists(): #check user exists
                post_data = Posts.objects.filter(id = post_id, is_deleted=False).values('id' ,'post_type', 'like_count','shock_count','smile_count','heart_count', 'title', 'description', 'post_file','post_image', 'file_type', 'is_entity','user_id')
               
                if post_data.exists(): #check post exists
                    post_user_id = post_data[0]['user_id']
                    shock_count = post_data[0]['shock_count']
                    smile_count = post_data[0]['smile_count']
                    heart_count = post_data[0]['heart_count']
                    like_count = post_data[0]['like_count']
                    user_point = user_data[0].get('user_point')
                    # total_count = shock_count+smile_count+heart_count+like_count

                    post_reaction_data = PostsReaction.objects.filter(post_id = post_id, user_id=user_id, post_track_status = False).values('id' ,'reaction', 'createdAt', 'updatedAt')
                    res=dict()
                    
                    if reaction=='1':
                        if post_reaction_data.exists(): #check post reaction exists
                            if post_reaction_data[0].get('reaction') == 1:
                                reaction_id = post_reaction_data[0]['id']
                                # if reaction == '1':
                                    #delete reaction
                                PostsReaction.objects.filter(id=reaction_id).delete()

                                #decrease like count
                                like_count = like_count - 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                PostsReaction.objects.filter(post_id=post_id, user_id=user_id).update(reaction=reaction)
                                Posts.objects.filter(id = post_id).update(like_count = like_count,total_count=total_count)
                                res = {'status' : 'True', 'detail' : 'Reaction deleted','like_count':like_count,'total_count':total_count,'reaction':reaction}    
                            
                            elif post_reaction_data[0].get('reaction') == 2:
                                like_count = like_count + 1
                                heart_count = heart_count - 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                PostsReaction.objects.filter(post_id=post_id, user_id=user_id).update(reaction=reaction)
                                Posts.objects.filter(id = post_id).update(heart_count = heart_count,like_count=like_count,total_count=total_count)
                                res= {'status' : 'True', 'detail' : 'Reaction inserted','like_count':like_count,'total_count':total_count,'reaction':reaction}

                            elif post_reaction_data[0].get('reaction') == 3:
                                like_count = like_count + 1
                                shock_count = shock_count - 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                PostsReaction.objects.filter(post_id=post_id, user_id=user_id).update(reaction=reaction)
                                Posts.objects.filter(id = post_id).update(shock_count = shock_count,like_count=like_count,total_count=total_count)
                                res= {'status' : 'True', 'detail' : 'Reaction inserted','like_count':like_count,'total_count':total_count,'reaction':reaction}                                
                            
                            elif post_reaction_data[0].get('reaction') == 4:
                                like_count = like_count + 1
                                smile_count = smile_count - 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                PostsReaction.objects.filter(post_id=post_id, user_id=user_id).update(reaction=reaction)
                                Posts.objects.filter(id = post_id).update(smile_count = smile_count,like_count=like_count,total_count=total_count)
                                res= {'status' : 'True', 'detail' : 'Reaction inserted','like_count':like_count,'total_count':total_count,'reaction':reaction}                            

                        else:
                            # if reaction == '1':
                                
                                #add reaction
                            reaction_data = PostsReaction(post_id=post_id, user_id=user_id,reaction=reaction, post_track_status =False)
                            reaction_data.save()
                            
                            #increase like count
                            like_count = like_count + 1
                            total_count = shock_count+smile_count+heart_count+like_count
                            Posts.objects.filter(id=post_id).update(like_count=like_count,total_count=total_count)
                            # Adding points
                            new_total_points=get_points(user_id,'post-reaction','like')
                            user_point+=new_total_points
                            JobUsers.objects.filter(id=user_id).update(user_point=user_point)

                            if  post_user_id and post_user_id != user_id:
                                send_push = True
                            res= {'status' : 'True', 'detail' : 'Reaction inserted','like_count':like_count,'total_count':total_count,'reaction':reaction}

                    elif reaction=='2':

                        if post_reaction_data.exists(): #check post reaction exists
                            if post_reaction_data[0].get('reaction') == 2:

                                reaction_id = post_reaction_data[0]['id']
                                #delete reaction
                                PostsReaction.objects.filter(id=reaction_id).delete()

                                #decrease like count
                                heart_count = heart_count - 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                Posts.objects.filter(id = post_id).update(heart_count = heart_count,total_count=total_count)
                                res = {'status' : 'True', 'detail' : 'Reaction deleted','heart_count':heart_count,'total_count':total_count,'reaction':reaction} 

                            elif post_reaction_data[0].get('reaction') == 1:
                                heart_count = heart_count + 1
                                like_count = like_count - 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                PostsReaction.objects.filter(post_id=post_id, user_id=user_id).update(reaction=reaction)
                                Posts.objects.filter(id = post_id).update(heart_count = heart_count,like_count=like_count,total_count=total_count)
                                res= {'status' : 'True', 'detail' : 'Reaction inserted','heart_count':heart_count,'total_count':total_count,'reaction':reaction}

                            elif post_reaction_data[0].get('reaction') == 3:
                                heart_count = heart_count + 1
                                shock_count = shock_count - 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                PostsReaction.objects.filter(post_id=post_id, user_id=user_id).update(reaction=reaction)
                                Posts.objects.filter(id = post_id).update(heart_count = heart_count,like_count=like_count,total_count=total_count)
                                res= {'status' : 'True', 'detail' : 'Reaction inserted','heart_count':heart_count,'total_count':total_count,'reaction':reaction}                                

                            elif post_reaction_data[0].get('reaction') == 4:
                                heart_count = heart_count + 1
                                smile_count = smile_count - 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                PostsReaction.objects.filter(post_id=post_id, user_id=user_id).update(reaction=reaction)
                                Posts.objects.filter(id = post_id).update(smile_count = smile_count,heart_count=heart_count,total_count=total_count)
                                res= {'status' : 'True', 'detail' : 'Reaction inserted','heart_count':heart_count,'total_count':total_count,'reaction':reaction}                            


                        else:
                            #add reaction
                            reaction_data = PostsReaction(post_id=post_id, user_id=user_id,reaction=reaction, post_track_status =False)
                            reaction_data.save()
                            
                            #increase like count
                            heart_count = heart_count + 1
                            total_count = shock_count+smile_count+heart_count+like_count

                            Posts.objects.filter(id=post_id).update(heart_count=heart_count,total_count=total_count)
                            # Adding points
                            new_total_points=get_points(user_id,'post-reaction','heart')
                            user_point+=new_total_points
                            JobUsers.objects.filter(id=user_id).update(user_point=user_point)
                            if  post_user_id and post_user_id != user_id:
                                send_push = True
                            res= {'status' : 'True', 'detail' : 'Reaction inserted','heart_count':heart_count,'total_count':total_count,'total_count':total_count,'reaction':reaction}

                    elif reaction=='3':

                        if post_reaction_data.exists(): #check post reaction exists
                            if post_reaction_data[0].get('reaction') == 3:
                                reaction_id = post_reaction_data[0]['id']
                                #delete reaction
                                PostsReaction.objects.filter(id=reaction_id).delete()

                                #decrease like count
                                shock_count = shock_count - 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                Posts.objects.filter(id = post_id).update(shock_count = shock_count,total_count=total_count)
                                res = {'status' : 'True', 'detail' : 'Reaction deleted','shock_count':shock_count,'total_count':total_count,'reaction':reaction}    

                            elif post_reaction_data[0].get('reaction') == 1:
                                shock_count = shock_count + 1
                                like_count = like_count - 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                PostsReaction.objects.filter(post_id=post_id, user_id=user_id).update(reaction=reaction)
                                Posts.objects.filter(id = post_id).update(shock_count = shock_count,like_count=like_count,total_count=total_count)
                                res= {'status' : 'True', 'detail' : 'Reaction inserted','shock_count':shock_count,'total_count':total_count,'reaction':reaction}

                            elif post_reaction_data[0].get('reaction') == 2:
                                shock_count = shock_count + 1
                                heart_count = heart_count - 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                PostsReaction.objects.filter(post_id=post_id, user_id=user_id).update(reaction=reaction)
                                Posts.objects.filter(id = post_id).update(heart_count = heart_count,shock_count=shock_count,total_count=total_count)
                                res= {'status' : 'True', 'detail' : 'Reaction inserted','shock_count':shock_count,'total_count':total_count,'reaction':reaction}                                

                            elif post_reaction_data[0].get('reaction') == 4:
                                shock_count = shock_count + 1
                                smile_count = smile_count - 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                PostsReaction.objects.filter(post_id=post_id, user_id=user_id).update(reaction=reaction)
                                Posts.objects.filter(id = post_id).update(smile_count = smile_count,shock_count=shock_count,total_count=total_count)
                                res= {'status' : 'True', 'detail' : 'Reaction inserted','shock_count':shock_count,'total_count':total_count,'reaction':reaction}                                                            

                        else:
                                
                                #add reaction
                                reaction_data = PostsReaction(post_id=post_id, user_id=user_id,reaction=reaction, post_track_status =False)
                                reaction_data.save()
                                
                                #increase like count
                                shock_count = shock_count + 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                Posts.objects.filter(id=post_id).update(shock_count=shock_count,total_count=total_count)
                                # Adding points
                                new_total_points=get_points(user_id,'post-reaction','shock')
                                user_point+=new_total_points
                                JobUsers.objects.filter(id=user_id).update(user_point=user_point)
                                if  post_user_id and post_user_id != user_id:
                                    send_push = True
                                res= {'status' : 'True', 'detail' : 'Reaction inserted','shock_count':shock_count,'total_count':total_count,'reaction':reaction}

                    elif reaction=='4':

                        if post_reaction_data.exists(): #check post reaction exists
                            if post_reaction_data[0].get('reaction') == 4:
                                reaction_id = post_reaction_data[0]['id']
                                #delete reaction
                                PostsReaction.objects.filter(id=reaction_id).delete()

                                #decrease like count
                                smile_count = smile_count - 1
                                total_count = shock_count+smile_count+heart_count+like_count
                                Posts.objects.filter(id = post_id).update(smile_count = smile_count,total_count=total_count)
                                res = {'status' : 'True', 'detail' : 'Reaction deleted','smile_count':smile_count,'total_count':total_count,'reaction':reaction}    

                            elif post_reaction_data[0].get('reaction') == 1:
                                smile_count = smile_count + 1
                                like_count = like_count - 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                PostsReaction.objects.filter(post_id=post_id, user_id=user_id).update(reaction=reaction)
                                Posts.objects.filter(id = post_id).update(smile_count = smile_count,like_count=like_count,total_count=total_count)
                                res= {'status' : 'True', 'detail' : 'Reaction inserted','smile_count':smile_count,'total_count':total_count,'reaction':reaction}

                            elif post_reaction_data[0].get('reaction') == 2:
                                smile_count = smile_count + 1
                                heart_count = heart_count - 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                PostsReaction.objects.filter(post_id=post_id, user_id=user_id).update(reaction=reaction)
                                Posts.objects.filter(id = post_id).update(heart_count = heart_count,smile_count=smile_count,total_count=total_count)
                                res= {'status' : 'True', 'detail' : 'Reaction inserted','smile_count':smile_count,'total_count':total_count,'reaction':reaction}                                

                            elif post_reaction_data[0].get('reaction') == 3:
                                shock_count = shock_count - 1
                                smile_count = smile_count + 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                PostsReaction.objects.filter(post_id=post_id, user_id=user_id).update(reaction=reaction)
                                Posts.objects.filter(id = post_id).update(smile_count = smile_count,shock_count=shock_count,total_count=total_count)
                                res= {'status' : 'True', 'detail' : 'Reaction inserted','smile_count':smile_count,'total_count':total_count,'reaction':reaction}

                        else:
                                #add reaction
                                reaction_data = PostsReaction(post_id=post_id, user_id=user_id,reaction=reaction, post_track_status =False)
                                reaction_data.save()
                                
                                #increase like count
                                smile_count = smile_count + 1
                                total_count = shock_count+smile_count+heart_count+like_count

                                Posts.objects.filter(id=post_id).update(smile_count=smile_count,total_count=total_count)
                                # Adding points
                                new_total_points=get_points(user_id,'post-reaction','shock')
                                user_point+=new_total_points
                                JobUsers.objects.filter(id=user_id).update(user_point=user_point)
                                if  post_user_id and post_user_id != user_id:
                                    send_push = True
                                res= {'status' : 'True', 'detail' : 'Reaction inserted','smile_count':smile_count,'total_count':total_count,'reaction':reaction}

                    else:
                        res = {'status' : 'False', 'detail' : 'Reaction does not exists'}
                            
                    # SEND PUSH NOTIFICATION on reaction from other user
                    # if send_push:
                    #     device_id=User[0].get('device_id')
                    #     payload = {"to": device_id,"notification": {"body": "The first message from the React Native and Firebase","title": "New reaction on your post ","content_available": True,"priority": "high"},"data": {"post_id": post_id}}
                    #     send_push_notification(payload)  
                    # END    
                    
                    return Response(res)
                    
                else:
                    return Response({
                        'status' : 'False',
                        'detail' : 'Post does not exists'
                    })
            else:
                return Response({
                    'status' : 'False',
                    'detail' : 'User does not exists'
                })

        else:
            return Response({
                'status' : 'False',
                'detail' : 'Data is required'
            })


class GetReactions(GenericAPIView):
    '''
    Get Post Reactions API
    '''
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        post_id=request.data.get('post_id',False)
        user_id=request.data.get('employee_id',False)
        user=JobUsers.objects.filter(employee_code=user_id).values('id')
        user_id=user[0].get('id')
        
        if(request.method=="POST"):
            postreaction = list(PostsReaction.objects.filter(user_id=user_id).values('reaction','post_id','user_id','createdAt','updatedAt').distinct())
            result=[]
            for i in postreaction:

                if i.get('reaction')==1:
                    reaction='Like'
                elif i.get('reaction')==2:
                    reaction='Heart'
                elif i.get('reaction')==3:
                    reaction='Shock'
                elif i.get('reaction')==4:
                    reaction='Smile'

                result.append({'status' : 'True', 'reaction_inserted' : reaction,'reaction_id':i.get('reaction'),'createdAt':i.get('createdAt'),'updatedAt':i.get('updatedAt'),'post_id':i.get('post_id'),'employee_id':i.get('user_id')})
            res={'status':False,'result':result}
        return Response(res)

# class Survey(GenericAPIView):
#     authentication_classes = (TokenAuthentication,) 

#     def post(self, request, *args, **kwargs):
#         if request.method == 'POST':
#             user_id = request.data.get('employee_id', False)
#             User=JobUsers.objects.filter(employee_code=user_id).values('id')
#             user_id=User[0].get('id')
#             # Polls
            
#             postids=[]
#             # for i in k:
#             #     postids.append(i.get('post_id'))
#             postids=list(set(postids))
#             queryset = list(Posts.objects.filter(post_type='poll', is_deleted=False).values('id', 'user_id__employee_name', 'user_id__userProfileImage', 'user_id__userProfileImage', 'user_id__id' ,'post_type', 'post_category__name','title', 'description', 'post_file', 'height', 'width', 'post_image', 'file_type', 'is_entity', 'status', 'verified_at', 'reactions','like_count', 'comment_count', 'createdAt', 'updatedAt','reactions').order_by('-createdAt'))
#             polls=[]
            
            

#             for i in queryset:
#                 k=list(PostActivities.objects.filter(user_id=user_id,post_id=i.get('id')).values('post_id'))
#                 answer_given=1
#                 if len(k)>0:
#                     answer_given=1
#                 data = i
#                 d1 = {"reactions": json.loads(i.get('reactions'))}
#                 # print(json.loads(i.get('reactions')))
#                 data.update(d1)
#                 # polls.append(data)
#                 # Calculate poll result
#                 result=list()
#                 sample=dict()
#                 total=len(PostActivities.objects.filter(option_name='poll_feedback',post_id=i.get("id")).values('option_val'))
#                 number=0
#                 for i in d1["reactions"]:
#                     # print(i)
#                     number+=1
                    
#                     answer=i.get('label')
#                     value=len(PostActivities.objects.filter(option_name='poll_feedback',post_id=i.get("id"),option_val=answer).values('option_val'))
#                     # percent=0
#                     if total==0:
#                         percent=0
#                     else:
#                         percent=(value/total)*100
#                     sample={"option_val":answer}
#                     # print(result)    
#                     sample={"percent":str(round(percent))+" %", str(number):round(percent)/100 ,'option_val':answer}

#                     result.append(sample)
#                 # End
#                 d2={"sample":result}
#                 data.update(d2)
#                 polls.append(data)
#                 print(polls)

#             # Quiz
#             k=list(QuizResult.objects.filter(job_user_id=user_id,is_deleted=False).values('quiz_id'))
#             quizids=[]
#             for i in k:
#                 quizids.append(i.get('quiz_id'))
#             quizids=list(set(quizids))
#             # print(quizids)
            
#             quiz=list(Quizes.objects.extra(select={'created_user' : "SELECT name FROM amrc_users WHERE amrc_users.id=amrc_quiz.created_by"}).exclude(Q(id__in=quizids)).filter(is_deleted=False).values('id','name','start_date','end_date','result_date','description', 'created_user', 'created_by','createdAt'))
            
            
#             result=[]
#             # for i in polls:
#             #     res=dict()
#             #     if i.get('post_type') == 'poll':
#             #         res.update({'type':'poll'})
#             #     res.update({'category':'survey','id':i.get('id'),
#             #         'employee_name':i.get('user_id__employee_name'),
#             #         'answer_given':answer_given,
#             #         'userProfileImage':i.get('user_id__userProfileImage'),
#             #         'title':i.get('title'),
#             #         'description':i.get('description'),
#             #         'reactions':i.get('reactions'),
#             #         'createdAt':i.get('createdAt'),
#             #         'answer':i.get('sample')})
#             #     result.append(res)
            
#             # for i in quiz:
#             #     res=dict()
#             #     res.update({'type':'quiz','category':'survey','id':i.get('id'),
#             #         'name':i.get('name'),
#             #         'description':i.get('description'),
#             #         'created_user':i.get('created_user'),
#             #         'total_like_count':20,
#             #         'Comment_count':10,
#             #         'userProfileImage':'http://52.66.228.107:8080/media/jobusers/userProfile_MmTUDee.jpg',
#             #         'createdAt':i.get('createdAt')})
#             #     result.append(res)



#             result=sorted(result, key = lambda item: item['createdAt'])
#             res={'status':True , 'result':polls+quiz}
#             return Response(res)



class Survey(GenericAPIView):
    authentication_classes = (TokenAuthentication,) 

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            # quiz_id = request.data.get('quiz_id', False)
            user_id = request.data.get('employee_id', False)

            User=JobUsers.objects.filter(employee_code=user_id).values('id')
            user_id=User[0].get('id')

            
            postids=[]
            # for i in k:
            #     postids.append(i.get('post_id'))
            # postids=list(set(postids))

            
            

            queryset = list(Posts.objects.extra(select={'created_user' : "SELECT name FROM amrc_users WHERE amrc_users.id=amrc_posts.created_by",'userProfileImage' : "SELECT user_logo FROM amrc_users WHERE amrc_users.id=amrc_posts.created_by"}).filter(post_type ='poll',is_deleted=False,user__isnull=True).values('id', 'created_user','userProfileImage' ,'post_type', 'post_category__name','title', 'description', 'createdAt', 'updatedAt','userProfileImage','reactions').order_by('-createdAt'))
            polls=[]
            for i in queryset:
                answer_given=0
                i["userProfileImage"]=settings.BASE_URL+"/media/"+i.get("userProfileImage")
                data = i
                k=list(PostActivities.objects.filter(user_id=user_id,post_id=data.get('id')).values('post_id'))
                if len(k)>0:
                    answer_given=1
                d1 = {"reactions": json.loads(i.get('reactions'))}
                # print(json.loads(i.get('reactions')))
                data.update(d1)
                # Calculate poll result
                result=list()
                sample=dict()
                total=len(PostActivities.objects.filter(option_name='poll_feedback',post_id=i.get("id")).values('option_val'))
                number=0
                for i in d1["reactions"]:
                    # print(i)
                    number+=1
                    
                    answer=i.get('label')
                    value=len(PostActivities.objects.filter(option_name='poll_feedback',post_id=data.get("id"),option_val=answer).values('option_val'))
                    percent=0
                    if total==0:
                        percent=0
                    else:
                        percent=(value/total)*100
                    sample={"option_val":answer}
                    # print(result)    
                    sample={"percent":str(round(percent))+" %", "percentage":round(percent)/100 ,'option_val':answer}

                    result.append(sample)
                # End
                d2={"sample":result}
                data.update(d2)
                d3={"answer_given":answer_given}
                data.update(d3)
                polls.append(data)
                # print(polls)

            # Quiz
            k=list(QuizResult.objects.filter(job_user_id=user_id,is_deleted=False).values('quiz_id'))
            quizids=[]
            for i in k:
                quizids.append(i.get('quiz_id'))
            quizids=list(set(quizids))
            print(quizids)
            
            quiz=list(Quizes.objects.extra(select={'created_user' : "SELECT name FROM amrc_users WHERE amrc_users.id=amrc_quiz.created_by",'userProfileImage' : "SELECT user_logo FROM amrc_users WHERE amrc_users.id=amrc_quiz.created_by"}).exclude(Q(id__in=quizids)).filter(is_deleted=False).values('id','name','start_date','end_date','userProfileImage','result_date','description', 'created_user', 'created_by','createdAt').order_by('-createdAt'))
            for i in quiz:
                i["userProfileImage"]=settings.BASE_URL+"/media/"+i.get("userProfileImage")

            res={'status':True , 'result':polls+quiz}
            return Response(res)

class CreateComment(GenericAPIView):
    '''
    Create Post Comment API
    '''
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
           
            post_id = request.data.get('post_id', False)
            user_id = request.data.get('employee_id', False)
            comment = request.data.get('comment', False)
            
            User=JobUsers.objects.filter(employee_code = user_id).values('id','user_point','device_token')
            user_id=User[0].get('id')

            old = Posts.objects.filter(id=post_id).values('id','comment_count')
            if old.exists():
                save_serialize = PostCommentSerializer(data=request.data)
                if save_serialize.is_valid(raise_exception=True):
                    save_serialize.save(
                                    post_id=post_id, 
                                    user_id=user_id,
                                    comment=comment,
                                    createdAt=timezones()
                            )
                    
                    #increase comment count
                comment_count=old[0]['comment_count']
                new_comment_count = comment_count + 1
                Posts.objects.filter(id=post_id).update(comment_count=new_comment_count)

                user_point=User[0].get('user_point')
                new_total_points=get_points(user_id,'post-comment','Post comment')
                user_point+=new_total_points
                JobUsers.objects.filter(id=user_id).update(user_point=user_point)
                # Comment Notification
                # post_data = Posts.objects.filter(id = post_id, is_deleted=False).values('id' ,'post_type', 'like_count', 'title', 'description', 'post_file','post_image', 'file_type', 'is_entity','user_id')
                if old.exists():
                    post_user_id = old[0]['id']
                    if post_user_id !=user_id:
                        device_id = User[0]['device_token']
                        payload = {"to": device_id,"notification": {"body": "The first message from the React Native and Firebase","title": "New comment on your Post","content_available": True,"priority": "high"},"data": {"post_id": post_id}}
                        send_push_notification(payload)

                res= {'status' : 'True', 'detail' : 'Comment added','comment_count':new_comment_count,'comment':comment}
            else :
                res={'status':False,'detail':"Post does not exist"}
        return Response(res)

class GetComments(GenericAPIView):
    '''
    Get Post Comment API
    '''
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        post_id=request.data.get('post_id',False)
        if(request.method=="POST"):
            post = Posts.objects.filter(id=post_id).values('comment_count')
           
            if post.exists():
                old = list(PostComments.objects.filter(post_id=post_id).values('user_id__employee_name','user_id__userProfileImage','comment','createdAt').distinct().order_by('-createdAt'))

                res= {'status' : 'True', 'comments' : old}
            else :
                res={'status':False,'detail':"Post does not have any comments"}
        return Response(res)

class GetPost(GenericAPIView):
    '''
    Get Post Comment API
    '''
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        post_id=request.data.get('post_id',False)

        if(request.method=="POST"):
            post = Posts.objects.filter(id=post_id,is_deleted=False).values('id', 'user_id__employee_name', 'user_id__userProfileImage', 'user_id__userProfileImage', 'user_id__id' ,'post_type', 'post_category__name','title', 'description', 'post_file', 'height', 'width', 'post_image', 'file_type', 'is_entity', 'status', 'verified_at', 'reactions','like_count', 'comment_count', 'createdAt', 'updatedAt','reactions')
            if post:
                res= {'status' : True, 'result' : post}
            else:
                res= {'status' : False, 'result' : 'post does not exist'}
        return Response(res)        
            
            
class PostLinkTrack(APIView):
    '''
    When user click on a link into a post
    '''
    authentication_classes = (TokenAuthentication,) 

    def post(self, request, *args, **kwargs):
        
        user_id           = request.data.get('user_id', False)
        post_id           = request.data.get('post_id', False)
        post_track_status = request.data.get('post_track_status', False)

        if user_id and post_id:
            
            user_data = JobUsers.objects.filter(id = user_id).values('id', 'job_role__name', 'employee_id','phone','first_name','middle_name','last_name','email','gender','user_id', 'is_active')
            
            if user_data.exists(): #check user exists
                
                post_data = Posts.objects.filter(id = post_id, is_deleted=False).values('id' ,'post_type', 'like_count', 'title', 'description', 'post_file','post_image', 'file_type', 'is_entity')
               
                if post_data.exists(): #check post exists
                    
                    post_reaction_data = PostsReaction.objects.filter(post_id = post_id, user_id=user_id, post_track_status = True).values('id')
                       
                    if post_reaction_data.exists(): #check post reaction exists
                        
                        return Response({
                            'status' : 'False',
                            'detail' : 'Tracking Data exists'
                        })
                        
                    else:
                        
                        #add Tracking data
                        tracking_data = PostsReaction(post_id=post_id, user_id=user_id,post_track_status=True)
                        tracking_data.save()
                        
                        return Response({
                            'status'            : 'True',
                            'detail'            : 'Tracking Data inserted',
                            'post_id'           : post_id,
                            'user_id'           : user_id,
                            'post_track_status' : True,
                        })

                    
                else:
                    return Response({
                        'status' : 'False',
                        'detail' : 'Post does not exists'
                    })
            else:
                return Response({
                    'status' : 'False',
                    'detail' : 'User does not exists'
                })

        else:
            return Response({
                'status' : 'False',
                'detail' : 'Data is required'
            })
            
# class PostCategories(APIView):
#     '''
#     Get Post Categories API
#     '''
#     authentication_classes = (TokenAuthentication,) 
#     def post(self, request):
#         print(authentication_classes)
#         if(request.method=="POST"):
#             post_category = PostCategory.objects.filter(status = True).values('id','name','status')
#             if post_category.exists():
#                 return Response({
#                     'status' : True, 
#                     'category' : post_category,
#                 })
#             else:
#                 return Response({
#                     'status' : False,
#                     'detail' : 'Category not exist'
#                 })     

class PostCategories(APIView):
    '''
    Report Post API
    '''
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
            user_id = request.data.get('employee_id', False)
        
            k=JobUsers.objects.filter(employee_code=user_id).values('language')
            print(list(k))
            language=k[0].get('language')
            if user_id:
                post_category = PostCategory.objects.filter(status = True, is_deleted = False).values('id','name','status','sequence').order_by('sequence')
                if post_category.exists():
                    if language:
                        post_category=[{"id":8,"name":"الكل","status":True},
                        {"id":1,"name":"أخبار الشركة","status":True},
                        {"id":4,"name":"أخبار الأقسام","status":True},
                        {"id":5,"name":"الأخبار العاجلة","status":True},
                        {"id":3,"name":"التقدير","status":True},
                        {"id":6,"name":"منطقة التعلم","status":True},
                        {"id":7,"name":"الإستبيان","status":True},
                        {"id":2,"name":"التنوع والشمول","status":True},
                        {"id":9,"name":"متجر المكافئات","status":True}]
                    #     for i in post_category:
                    #         trans=Translator()
                    #         name=i.get('name')
                    #         name1=trans.translate(name,src='en',dest='ar')
                    #         i["name"]=str(name1.text)

                    return Response({'status' : True, 'category' : post_category})
                        # return Response(res)
                else:
                    return Response({'status' : False, 'detail' : 'Category not exist'})
            else:
                return Response({'status' : False, 'detail' : 'User id is required'})
     

class getPostDetail(APIView):
    '''
    Report Post API
    '''
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
            
            post_categoryId = request.data.get('category_id', False)
            userId = request.data.get('employee_id', False)
            user=JobUsers.objects.filter(employee_code=userId).values('id','language')
            userId=user[0].get('id')
            language=user[0].get('language')

            if post_categoryId:
                category = PostCategory.objects.filter(id=post_categoryId).values('id','name')
                post_name=category[0].get('name')
                # queryset2 = Posts.objects.filter(post_category__name=post_name,approve_status=1,post_language=language,is_deleted=False).values('id', 'title', 'description','post_type','user_id__employee_name','user_id__userProfileImage', 'user_id__employee_code','post_category__name','post_language' ,'post_image', 'post_file', 'file_type', 'taggedusers', 'like_count','shock_count','smile_count','heart_count','comment_count','total_count','approve_status','createdAt','status')
                
                queryset1 = list(Posts.objects.extra(select={'user_id__employee_name' : "SELECT name FROM amrc_users WHERE amrc_users.id=amrc_posts.created_by",'user_id__userProfileImage' : "SELECT user_logo FROM amrc_users WHERE amrc_users.id=amrc_posts.created_by"}).exclude(post_type='birthday').filter(~Q(post_type ='quiz'), Q(is_deleted=False),post_category__name=post_name,user__isnull=True,approve_status=1).values('id', 'user_id__employee_name','user_id__userProfileImage', 'user_id__employee_code', 'post_type', 'title', 'description', 'post_file', 'post_category__name', 'post_image', 'file_type', 'status', 'approve_status', 'like_count','shock_count','smile_count','heart_count','total_count','created_by' ,'comment_count', 'createdAt','updatedAt').order_by('-id') )
                for i in queryset1:
                    title=i.get('title')
                    description=i.get('description')
                    titl=''
                    desc=''
                    if language: # 0 = english and 1 = arabic
                        
                        titl=title.get('arabic')
                        if titl=='':
                            titl=title.get('english')
                        
                        desc=description.get('arabic')
                        if desc=='':
                            desc=description.get('english')
                    else:
                        titl=title.get('english')
                        desc=description.get('english')
                    i['title']=titl
                    i['description']=desc
                
                queryset2 = list(Posts.objects.exclude(post_type='birthday').filter(~Q(is_deleted=False),post_category__name=post_name,approve_status=1,user__isnull=False).values('id', 'user_id__employee_name','user_id__userProfileImage', 'user_id__employee_code', 'post_type', 'title', 'description', 'post_file', 'post_category__name', 'post_image', 'file_type','like_count','shock_count','smile_count','heart_count','total_count' ,'comment_count', 'createdAt', 'updatedAt').order_by('-id') )
                for i in queryset2:
                    title=i.get('title')
                    description=i.get('description')

                    titl=title.get('english')
                    desc=description.get('english')
                    i['title']=titl
                    i['description']=desc
                queryset3=queryset2+queryset1
                queryset3=sorted(queryset3, key = lambda item: item['createdAt'],reverse=True)                
                
                for item1 in queryset3:
                    
                    post_id=item1.get('id')
                    comments=list(PostComments.objects.filter(post_id=post_id).values('user_id__employee_name','user_id__userProfileImage','comment').order_by('-createdAt'))
                    if len(comments)<2:
                        item1.update({"comments":comments})
                    else:
                        comments=list(PostComments.objects.filter(post_id=post_id).values('user_id__employee_name','user_id__userProfileImage','comment').order_by('-createdAt'))[0:2]    
                        item1.update({"comments":comments})

                if category.exists():
                    return Response({'status' : True, 'results' : queryset3})
                else:
                    return Response({'status' : False, 'detail' : 'Invalid Category id'})
            else:
                return Response({'status' : False, 'detail' : 'Category id is required'})
 
# class CreatePostComment(APIView):
#     '''
#     Create Post Comment API
#     '''
#     authentication_classes = (TokenAuthentication,) 
#     def post(self, request, *args, **kwargs):
#         if(request.method=="POST"):
           
#             post_id = request.data.get('post_id', False)
#             user_id = request.data.get('user_id', False)
#             option_name = request.data.get('option_name', False)
#             user_data = JobUsers.objects.filter(id = user_id).values('id', 'job_role__name', 'employee_id','phone','first_name','middle_name','last_name','device_id','email','gender','user_id','store_id','sekret_key','user_type','start_date','term_date','primary_brand','multi_brand','work_phone','home_phone','fax','country','concept','bmu','record_type','job_role','franchise_id','department','manager_id', 'vender', 'gpn', 'user_point', 'is_staff', 'is_active', 'dateOfBirth', 'userProfileImage', 'userDescription')
#             if option_name == 'dislike':
#                 if post_id and user_id:
#                     old = PostActivities.objects.filter(post_id=post_id,user_id=user_id,option_name='like')
#                     if old.exists():
#                         old.delete()
#                         return Response({'status' : True, 'detail' : 'Disliked successfully'})
#                     else:
#                         return Response({'status' : False, 'detail' : 'No record found'})
               
#                 else:
#                     return Response({'status' : False, 'detail' : 'Post id and User id are required'})
               
#             else:
#                 save_serialize = PostActivitiesSerializer(data=request.data)
#                 if save_serialize.is_valid(raise_exception=True):

#                     old = PostActivities.objects.filter(post_id=post_id,user_id=user_id,option_name='like')
#                     if old.exists():
#                         old.delete()


#                     old = Posts.objects.filter(id__iexact = post_id)
#                     # old = Posts.objects.filter(id=post_id).values('comment_count')
#                     if old.exists():
#                         count = old.first().comment_count
#                         # return Response({"error": count})
#                         t = Posts.objects.get(id=post_id)
#                         t.comment_count = count + 1
#                         t.save() # this will update only
#                     save_serialize.save()
#                     created_data = save_serialize.data
                    
#                     # SEND PUSH NOTIFICATION after comment 
#                     if option_name == 'comment':
#                         if user_data.exists():
#                             post_data = Posts.objects.filter(id = post_id, is_deleted=False).values('id' ,'post_type', 'like_count', 'title', 'description', 'post_file','post_image', 'file_type', 'is_entity','user_id')
#                             if post_data.exists():
#                                 post_user_id = post_data[0]['user_id']
#                                 if post_user_id !=user_id:
#                                     device_id = user_data[0]['device_id']
#                                     payload = {"to": device_id,"notification": {"body": "The first message from the React Native and Firebase","title": "New comment on your Post","content_available": True,"priority": "high"},"data": {"post_id": post_id}}
#                                     send_push_notification(payload) 
#                     #END
                    
#                     user_detail = JobUsers.objects.filter(id=user_id).values('first_name', 'middle_name', 'last_name', 'userProfileImage')
#                     if user_detail.exists():
#                         user_detail =user_detail.first()
#                         created_data['user_id__first_name'] = user_detail['first_name']
#                         created_data['user_id__middle_name'] = user_detail['middle_name']
#                         created_data['user_id__last_name'] = user_detail['last_name']
#                         created_data['user_id__userProfileImage'] = user_detail['userProfileImage']
#                     return Response(created_data, status=status.HTTP_201_CREATED)
#                 else:
#                     return Response({
#                     'status' : False,
#                     'detail' : 'HTTP_400_BAD_REQUEST'
#                     })
#         else:
#             return Response("", status=404)

class DeletePost(APIView):
    '''
    Create Post Comment API
    '''
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
            post_id = request.data.get('post_id', False)
            if post_id:
                old = Posts.objects.filter(id__iexact = post_id)
                if old.exists():
                    PostActivities.objects.filter(post_id=post_id).delete()
                    PostComments.objects.filter(post_id=post_id).delete()
                    PostsReaction.objects.filter(post_id=post_id).delete()
                    exist_files = old[0].post_file
                    exist_images = old[0].post_image
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
                    old.delete()
                    return Response({'status' : True, 'detail' : 'Post deleted successfully'})
                else:
                    return Response({'status' : False, 'detail' : 'Invalid Post id'})
            else:
                return Response({'status' : False, 'detail' : 'Post id is required'})


class HidePost(APIView):
    '''
    Hide Post API
    '''
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
            post_id = request.data.get('post_id', False)
            user_id = request.data.get('user_id', False)
            if post_id and user_id:
                old = Posts.objects.filter(id = post_id, user_id = user_id).values('id')
                if old.exists():

                    save_serialize = PostActivitiesSerializer(data=request.data)
                    if save_serialize.is_valid(raise_exception=True):
                        queryset = PostActivities.objects.filter(post_id=post_id, user_id=user_id, option_name='post_hide', option_val='1').values('id')
                       
                        if queryset.exists():
                            return Response({'status' : False, 'detail' : 'This Post already hidden'})
                        else:
                            save_serialize.save()
                            return Response({'status' : True, 'detail' : 'Post hide successfully'})
                    else:
                        return Response({'status' : False, 'detail' : 'Invalid Post id'})
            else:
                return Response({'status' : False, 'detail' : 'Post id and user id are required'})



class ReportPost(APIView):
    '''
    Report Post API
    '''
    # authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
            post_id = request.data.get('post_id', False)
            user_id = request.data.get('user_id', False)
            if post_id and user_id:
                old = Posts.objects.filter(id = post_id, user_id = user_id).values('id')
                if old.exists():

                    save_serialize = PostActivitiesSerializer(data=request.data)
                    if save_serialize.is_valid(raise_exception=True):
                        # queryset = PostActivities.objects.filter(post_id=post_id, user_id=user_id, option_name='post_report', option_val='1').values('id')
                       
                        # if queryset.exists():
                        #     return Response({'status' : False, 'detail' : 'This Post already hidden'})
                        # else:
                        save_serialize.save()
                        return Response({'status' : True, 'detail' : 'Post Reported successfully'})
                    else:
                        return Response({'status' : False, 'detail' : 'Invalid Post id'})
            else:
                return Response({'status' : False, 'detail' : 'Post id and user id are required'})

class GetPoll(APIView):
    '''
    Report Post API
    '''
    # authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
            userId = request.data.get('employee_id', False)
            User=JobUsers.objects.filter(employee_code=userId).values('id')
            userId=User[0].get('id')
            if userId:
               
                post_ids = []
                queryset = PostActivities.objects.filter(user_id=userId, option_name = 'post_hide', option_val = '1').values('post_id').distinct()
                old_posts = list(PostActivities.objects.filter(option_name='poll_feedback' ,user_id=userId).values('post_id').distinct())

                for item in old_posts:
                    post_ids.append(item['post_id'])
               
                print(post_ids)
                # queryset = Posts.objects.filter(post_type='poll').values('id', 'user_id__first_name', 'user_id__userProfileImage', 'post_type', 'title', 'description', 'post_file', 'post_image', 'file_type', 'height', 'width', 'is_entity', 'status', 'verified_at', 'reactions', 'like_count', 'comment_count', 'created_at', 'updated_at').order_by('-id')

                queryset = Posts.objects.filter(post_type='poll', is_deleted=False).values('id', 'user_id__employee_name', 'user_id__userProfileImage', 'user_id__userProfileImage', 'user_id__id' ,'post_type', 'post_category__name','title', 'description', 'post_file', 'height', 'width', 'post_image', 'file_type', 'is_entity', 'status', 'verified_at', 'reactions','like_count', 'comment_count', 'createdAt', 'updatedAt','reactions').exclude(id__in=post_ids).order_by('-id')               
                data = queryset[0]
                d1 = {"reactions": json.loads(queryset[0]['reactions'])}
                print(json.loads(queryset[0]['reactions']))
                data.update(d1)
                                
                if queryset.exists():
                    return Response({'status' : True, 'data' : data})
                else:
                    return Response({'status' : False, 'detail' : 'No Poll available'})
            else:
                return Response({'status' : False, 'detail' : 'User id is required'})

class UpdatePollFeedback(APIView):
    '''
    Update Poll Feedback API
    '''
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
            post_id = request.data.get('post_id', False)
            user_id = request.data.get('employee_id', False)
            option_name = 'poll_feedback'
            option_val=request.data.get('option_val', False)

            User=JobUsers.objects.filter(employee_code=user_id).values('id','user_point')
            user_id=User[0].get('id')

            if post_id and user_id:
                if(option_name == 'poll_feedback'):
                    old = Posts.objects.filter(id = post_id).values('id')
                    if old.exists():

                        save_serialize = PostActivitiesSerializer(data=request.data)
                        if save_serialize.is_valid(raise_exception=True):
                            queryset = PostActivities.objects.filter(post_id=post_id, user_id=user_id, option_name='poll_feedback').values('id')
                        
                            if queryset.exists():
                                return Response({'status' : False, 'detail' : 'You have already submitted feedback for this poll','post_id':post_id})
                            else:
                                save_serialize.save(post_id=old[0].get('id'),user_id=user_id,option_name='poll_feedback',option_val=option_val)
                                user_point=User[0].get('user_point')
                                new_total_points=get_points(user_id,'polls','Poll feedback')
                                user_point+=new_total_points
                                JobUsers.objects.filter(id=user_id).update(user_point=user_point)

                                return Response({'status' : True, 'detail' : 'Your feedback submitted successfully','post_id':post_id})
                    else:
                        return Response({'status' : False, 'detail' : 'Invalid Post id'})
                else:
                    return Response({'status' : False, 'detail' : 'Invalid option name'})
            else:
                return Response({'status' : False, 'detail' : 'Post id and user id are required'})

class GetStarOfTheMonth(APIView):
    '''
    Report Post API
    '''
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
            # userId = request.data.get('user_id', False)
            yearForFilter = timezones(). year
            year = request.data.get('year', False)
            if year:
                yearForFilter = year
            #    yearfor
                # t = CustomUser.objects.get(id=4)
                # t.first_name = 'Rajiv'
                # t.last_name = 'Pandey'
                # t.save() # this will update only

                queryset = StarOfTheMonth.objects.filter(selected_date__year=yearForFilter).values('id', 'user_id__first_name', 'user_id__middle_name', 'user_id__last_name', 'user_id__userProfileImage', 'user_id' , 'title', 'award_lebel', 'selected_date', 'created_at', 'updated_at').order_by('award_lebel')
                # queryset = StarOfTheMonth.objects.filter(selected_date__year=2020)
                print(queryset)
                if queryset.exists():
                    return Response({'status' : True, 'data' : queryset})
                else:
                    return Response({'status' : False, 'detail' : 'No Awarded users available'})
            else:
                return Response({'status' : False, 'detail' : 'Year is required'})




class GetNotifications(APIView):
    '''
    Report Post API
    '''
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
            userId = request.data.get('employee_id', False)
            user=JobUsers.objects.filter(employee_code=userId).values('id')
            userId=user[0].get('id')
            if userId:

                # dddddddd = Notification.objects.raw("select * from account_notification")

                # dddddddd = Notification.objects.raw("select * from account_notification t1 where t1 .to_user_id IN ( 0 , 1 ) AND t1 .from_user_id_id != 1 AND t1 .id != ( select  count ( t1 .p_id )  from account_notification t2 where t2 .p_id = t1 .id )")


                
                notification_ids = []

                # for noti in Notification.objects.raw("select t1.id from amrc_notification t1 JOIN amrc_notification t2 on t1.id = t2.p_id where t1.createdAt > current_date"):
                #     notification_ids.append(noti.id)

                # print(notification_ids)
                queryset = Notification.objects.filter(~Q(from_user_id_id =userId),Q(to_user_id =0) | Q(to_user_id=userId), n_type='normal', createdAt__gte=timezones().date()-timedelta(days=15)).values('id', 'title', 'sub_title','from_user_id__userProfileImage', 'data', 'detail', 'createdAt', 'updatedAt').order_by('-id')
                # queryset = Notification.objects.filter(~Q(from_user_id_id =userId),Q(to_user_id =0) | Q(to_user_id=userId), n_type='normal', createdAt__gte=timezones().date()-timedelta(days=15)).values('id', 'title', 'sub_title','from_user_id__userProfileImage', 'data', 'detail', 'createdAt', 'updatedAt').order_by('-id')

                return Response({
                        'status' : True, 
                        'count':len(queryset),
                        'notifications' : queryset,
                    })



                # old_noti = list(Notification.objects.raw("select t1.id from account_notification t1 JOIN account_notification t2 on t1.id = t2.p_id where t1.created_at > current_date - interval '15' day "))
                # serializer_old = NotificationSerializer(old_noti, many=True) 
            
                # return Response({
                #         'status' : True, 
                #         'notifications' : serializer_old.data,
                #     })

            else:
                return Response({'status' : False, 'detail' : 'User id is required'})

class GetSystemNotifications(APIView):
    '''
    Report Post API
    '''
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
            userId = request.data.get('user_id', False)
            User=JobUsers.objects.filter(employee_code=userId).values('id')
            userId=User[0].get('id')
            if userId:

                notification_ids = []

                for noti in Notification.objects.raw("select t1.id from account_notification t1 JOIN account_notification t2 on t1.id = t2.p_id where t1.created_at > current_date - interval '25' day "):
                    notification_ids.append(noti.id)
                # entitydata = CustomUser.objects.filter(id = userId).values('entity_id').first()
                # entity_id = entitydata['entity_id'] if entitydata['entity_id'] else 0
                # print(entity_id)
                queryset = Notification.objects.filter(~Q(from_user_id_id =userId),Q(to_user_id =0) | Q(to_user_id=userId), n_type='update', created_at__gte=timezones().date()-timedelta(days=25)).values('id', 'from_user_id__userProfileImage', 'title','sub_title', 'data', 'created_at', 'updated_at').exclude(id__in=notification_ids).order_by('-id')

                return Response({
                        'status' : True, 
                        'notifications' : queryset,
                    })
            else:
                return Response({'status' : False, 'detail' : 'User id is required'})
         

# class CreatePostComment(APIView):
#     '''
#     Create Post Comment API
#     '''
#     authentication_classes = (TokenAuthentication,) 

#     def post(self, request, *args, **kwargs):
#         if(request.method=="POST"):
           
#             post_id = request.data.get('post_id', False)
#             save_serialize = PostActivitiesSerializer(data=request.data)
#             if save_serialize.is_valid(raise_exception=True):

#                 old = Posts.objects.filter(id__iexact = post_id)
#                 # old = Posts.objects.filter(id=post_id).values('comment_count')
#                 if old.exists():
#                     count = old.first().comment_count
#                     # return Response({"error": count})
#                     t = Posts.objects.get(id=post_id)
#                     t.comment_count = count + 1
#                     t.save() # this will update only
              
#                 save_serialize.save()
#                 return Response({
#                 'status' : True,
#                 'detail' : save_serialize.data
#                 })
#                 # return Response(save_serialize.data, status=status.HTTP_201_CREATED)
#             else:
#                 return Response({
#                 'status' : False,
#                 'detail' : 'HTTP_400_BAD_REQUEST'
#                 })
#         else:
#             return Response("", status=404)

def get_user_points(user_id,user_points):
    total_point =0
    user_point =0
    old = JobUsers.objects.filter(id = user_id).values('user_point')
    if old.exists():
        user_point = old.first()['user_point']
            
    post_count = Posts.objects.filter(user_id = user_id, post_type = 'post').count()
    post_points = settings.POINTS_ON_ACTIONS['new_post'] * post_count

    comment_count = PostActivities.objects.filter(user_id = user_id, option_name = 'comment').count()
    comment_points = settings.POINTS_ON_ACTIONS['comment'] * post_count

    like_count = PostActivities.objects.filter(user_id = user_id, option_name = 'like').count()
    like_points = settings.POINTS_ON_ACTIONS['like'] * like_count

    gif_comment_count = PostActivities.objects.filter(user_id = user_id, option_name = 'comment_emoji').count()
    gif_comment_points = settings.POINTS_ON_ACTIONS['gif_comment'] * gif_comment_count

    total_point = post_points + comment_points + like_points + gif_comment_points
    
    return total_point
            

def send_otp(phone):
        if phone:
            # key = random.randint(999,9999)
            key = '1234'
            return key
        else:
            return False


def add_notification(ntype, from_user_id, to_user_id='', to_user_type='', noti_type='',title='',sub_title='', data='',entity_id=0):
    # old = PostActivities.objects.filter(user_id__iexact = user_id, user_id__iexact = user_id).count()
    if from_user_id != "":
        user_detail = JobUsers.objects.filter(id = from_user_id).values('job_role').first()
        
        # user_detail = CustomUser.objects.all()
        # ~ print(settings.POINTS_ON_ACTIONS)
        to_user_id = 0 if to_user_id=='' else to_user_id
        to_user_type = '' if to_user_type=='' else to_user_type
        noti_type = 'global' if noti_type=='global' else 'local'
        title = title
        print('ntype=>',ntype)
        print('from_user_id=>',from_user_id)
        print('user_detail=>',user_detail['job_role'])
        print('to_user_id=>',to_user_id)
        print('to_user_type=>',to_user_type)
        print('noti_type=>',noti_type) 
        print('title=>',title)
        print('sub_title=>',sub_title)
        print('data=>',data)
        # save_serialize = NotificationSerializer(data=request.data)

        notification_data = Notification(n_type=ntype, from_user_id_id=from_user_id,from_user_type=user_detail['job_role'],to_user_id=to_user_id,to_user_type=to_user_type,noti_type=noti_type,title=title,sub_title=sub_title,detail=data)
        notification_data.save()
        return "notification added"
    else:
        pass


def get_user_badge(point):
    user_badge ='No points'
    if point >= 50  and point<250:
        user_badge = 'Smoky Red Newbie' 
    elif point >=250 and point < 500:
        user_badge = 'Regular Popcorn Lover'  
    elif point >=500:
        user_badge = 'Zinger Maniac' 
    elif point >=600:
        user_badge = 'Hot & Crispy Superstar' 
    return user_badge

def get_device_id(user_id):
    user_data = JobUsers.objects.filter(id = user_id).values('id', 'job_role__name', 'employee_id','phone','first_name','middle_name','last_name','device_id')
    device_id = ''
    if user_data.exists():
        device_id = user_data[0]['device_id']

    return device_id


def get_points(user_id,slug,point_action):
    points=Points.objects.filter(slug=slug).values('id','title','slug','points','createdAt','brand_id')
    job_user_point=Job_User_Points_Log(user_id=user_id,point_id=points[0].get('id'),point_action=point_action,action_type='plus',point_desc=points[0].get('title'),point=points[0].get('points'))
    job_user_point.save()
    return points[0].get('points')


class TestNotif(APIView):
    
    def get(self, request, *args, **kwargs):
        # ~ device_id = 'fW2PZ0W87khan_Z4t42aKn:APA91bEWWU4bX2h3h3N_VYGbZpFYi4N9WB0Z_iFprRteZMIU1RysGcW1n7xrFufo-8MzkRCbxZtgVqxsXJGLUDL9iGS751aeFgffvLgRfC-14DJyB3sd6AXLAaIP498xCbKRydoG_J5W'
        device_id = '4B100195-C662-4E3D-86B4-8C83DA4F6945'
        payload = {"to": device_id,"notification": {"body": "The first message from the React Native and Firebase","title": "New reaction on your post ","content_available": True,"priority": "high"},"data": {"post_id": 21}}
        resp = send_push_notification(payload)
        print('resp', resp)
