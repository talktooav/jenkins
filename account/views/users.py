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

from jobusers.models import JobUsers, PhoneOTP
from post.models import Posts, PostActivities, PostsReaction
from rewards.models import StarOfTheMonth
from pushNotification.models import Notification
from moderation.models import Moderation
from postcategory.models import PostCategory

from account.serializers import CustomUserSerializer, PostActivitiesSerializer, WishUserBirthdaySerializer, PostSerializer, NotificationSerializer
from account.backends import TokenAuthentication


from americana.utils import timezones
from datetime import timedelta
from PIL import Image
import io

import jwt
import base64
from django.core.files.base import ContentFile
import json
from americana.utils import send_push_notification
from americana.files import file_upload, file_from_url


USER_PROFILE_FILE_LOCATION = '/root/americana/Americana/americana/static_cdn/upload_media/jobusers/'
USER_PROFILE_UPLOAD_PATH   = '/media/jobusers/'


class Login(APIView):
    '''
    If you have received otp, post a request with phone and that otp and you will be redirected to go further
    '''

    def post(self, request, *args, **kwargs):

        # ~ phone      = request.data.get('phone', False)
        username        = request.data.get('username', False) #E_ID
        password        = request.data.get('password', False) #DOB(YYYY-MM-DD)
        market          = request.data.get('country', False)  #Country
        language        = request.data.get('language',False)  #Language
        fcm_token       = request.data.get('fcm_token',False)
        device_type     = request.data.get('device_type',False)
        device_id       = request.data.get('device_id',False)
        print('token',fcm_token,'Id',device_id,'type',device_type)

        if language :
            JobUsers.objects.filter(employee_code__iexact = username,market=market).update(language=language,device_id=device_id,device_token=fcm_token)

        if username and password and market:
            dob   = password
            userdata = JobUsers.objects.filter(employee_code__iexact = username) 
            if userdata.exists():
          
                user_data = JobUsers.objects.filter(employee_code__iexact = username).values('id', 'employee_code','employee_name','market','date_of_birth', 'userProfileImage','is_logged')
                
                sample=['http://52.66.228.107:8080/media/country/Artboard1.png','http://52.66.228.107:8080/media/country/Artboard3.png','http://52.66.228.107:8080/media/country/Artboard4.png','http://52.66.228.107:8080/media/country/Artboard5.png']
                avatar= [ {'avatar' : sample[0]} , {'avatar' : sample[1]} , {'avatar' : sample[2]},{'avatar' : sample[3]} ]

                old_dob = user_data[0]['date_of_birth']
                emp_code=user_data[0]['employee_code']
                mkt=user_data[0]['market']
                user_id = user_data[0]['id']
                isLoggedStatus = user_data[0]['is_logged']
                if (str(old_dob) == str(dob)) &(str(username)==str(emp_code)) & (str(mkt)==str(market)):
                    user = authenticate(e_code=emp_code,password=password)
                    payload = {
                            'id'    : user_id,
                            'e_code' : emp_code,
                        }
                    # encoded_jwt = {'token' : jwt.encode(payload, 'SECRET_KEY') }
                    encoded_jwt = jwt.encode(payload, 'SECRET_KEY')
                    
                    #update login time and Regisration id
                    if emp_code:
                        JobUsers.objects.filter(id=user_id).update(logged_in_time = timezones())
                    else:
                        JobUsers.objects.filter(id=user_id).update(logged_in_time = timezones())
                    return Response({
                                    'status' : True, 
                                    'detail' : 'Password matched, kindly proceed to add profile information',
                                    'token' : encoded_jwt,
				    'avatars':avatar,
                                    'profile_data' : user_data[0],
                                    'isLoggedStatus' : isLoggedStatus,
                                    })
                else:
                    
                    return Response({
                        'status' : False, 
                        'detail' : 'Password incorrect, please try again'
                    })
            else:
                return Response({
                    'status' : False, 
                    'detail' : 'Employee does not exists'
                })
                    
        else:
            return Response({
                'status' : 'False',
                'detail' : 'Either username or password was not recieved in Post request'
            })

# class Country(APIView):
#     def get(self, request, *args, **kwargs):

#         country_name=['UAE','Egypt','Saudi Arabia','Kuwait','Bahrain','Jordan','Morocco','Lebanon','Iraq']
#         country_flag=[
#         "http://52.66.228.107:8080/media/country/United_Arab_Emirates-100.jpg",
#         "http://52.66.228.107:8080/media/country/Egypt-100.jpg",
#         "http://52.66.228.107:8080/media/country/Saudi_Arabia-100.jpg",
#         "http://52.66.228.107:8080/media/country/Kuwait-100.jpg",
#         "http://52.66.228.107:8080/media/country/Bahrain-100.jpg",
#         "http://52.66.228.107:8080/media/country/Jordan-100.jpg"
#         "http://52.66.228.107:8080/media/country/Morocco-100.jpg",
#         "http://52.66.228.107:8080/media/country/Lebanon-100.jpg",
#         "http://52.66.228.107:8080/media/country/Iraq-100.jpg",
#         ]
#         sample=[{'country':country_name[0],
#                 'flag':country_flag[0]
#                 },{'country':country_name[1],
#                 'flag':country_flag[1]
#                 },{'country':country_name[2],
#                 'flag':country_flag[2]
#                 },{'country':country_name[3],
#                 'flag':country_flag[3]
#                 },{'country':country_name[4],
#                 'flag':country_flag[4]
#                 },{'country':country_name[5],
#                 'flag':country_flag[5]
#                 },{'country':country_name[6],
#                 'flag':country_flag[6]
#                 },{'country':country_name[7],
#                 'flag':country_flag[7]
#                 },{'country':country_name[8],
#                 'flag':country_flag[8]
#                 }]
#         if(request.method=="GET"):
#             return Response(sample)


class GetProfile(APIView):
    authentication_classes = (TokenAuthentication,) 

    def post(self, request, *args, **kwargs):

        # employee_id = request.query_params.get('employee_id')
        employee_id = request.data.get('employee_id', False)

        if employee_id:
            user_data = JobUsers.objects.filter(employee_code = employee_id).values('id', 'employee_code','employee_name','userProfileImage','is_logged','date_of_birth','job_role__name','gender','market','hire_date','nationality','createdAt')
            if user_data.exists():
                # queryset = Posts.objects.filter(is_deleted=False, user_id=user_data[0]['id']).values('id','user_id__first_name', 'user_id__userProfileImage', 'post_type', 'title', 'description', 'post_file', 'post_image', 'file_type', 'height', 'width', 'is_entity', 'status', 'verified_at', 'reactions', 'like_count', 'comment_count', 'created_at', 'updated_at').order_by('-id')
                user_detail = user_data[0]
                # user_points = get_user_points(user_detail['id'], user_detail['user_point'])
                # user_badge = get_user_badge(user_points)
                user_profile_data = user_detail 
    

                # user_profile_data['user_badge'] = user_badge 
                # user_profile_data['user_point'] = user_points 

                # pending_posts = Posts.objects.filter(~Q(post_type ='poll'), user_id=user_detail['id'], approve_status=0, is_deleted=False).values('id', 'user_id__first_name', 'user_id__middle_name', 'user_id__last_name', 'user_id__userProfileImage', 'user_id_id' ,'post_type', 'title', 'description', 'post_file', 'height', 'width', 'post_image', 'file_type', 'is_entity', 'status', 'verified_at', 'reactions','like_count', 'comment_count', 'created_at', 'updated_at').order_by('-id')[:6]
                # post_cat = [2,3]

                # special_posts = Posts.objects.filter(~Q(post_type ='poll'), tagged_users__contains = [user_detail['id']], approve_status=1, is_deleted=False, post_category__in = post_cat).values('id', 'user_id__first_name', 'user_id__middle_name', 'user_id__last_name', 'user_id__userProfileImage', 'user_id_id' ,'post_type', 'title', 'description', 'post_file', 'height', 'width', 'post_image', 'file_type', 'is_entity', 'status', 'verified_at', 'reactions','like_count', 'comment_count', 'created_at', 'updated_at').order_by('-id')

                # user_recognition = StarOfTheMonth.objects.filter(user_id=user_detail['id']).values('id', 'user_id' , 'title', 'award_lebel', 'selected_date', 'created_at', 'updated_at').order_by('-selected_date')

                
                # print(user_data[0]['user_point'])
                return Response({
                    'status' : True, 
                    'profile_data' : user_profile_data,
                    # 'user_recognition' : user_recognition,
                    # 'pending_posts' : pending_posts,
                    # 'special_posts' : special_posts,

                })
            else:
                return Response({
                    'status' : 'False',
                    'detail' : 'Incorrect Employee ID'
                })

        else:
            return Response({
                'status' : 'False',
                'detail' : 'Employee ID is required'
            })

class UpdateProfile(APIView):
    '''
    Upload user image
    '''
    authentication_classes = (TokenAuthentication,) 

    # queryset = CustomUser.objects.all()
    # serializer_class = CustomUserSerializer
    parser_classes = (MultiPartParser, FormParser, FileUploadParser,)

    def post(self, request, *args, **kwargs):
        
        # ~ profileImg = request.data.get('profileImg', False)
        employee_id = request.data.get('employee_id', False)
        file_img = False
        file_url = False
        if request.FILES:
            file_img = True
            profileImg = request.FILES['profileImg']
        else:
            file_url = True
            profileImg = request.data.get('profileImg', False)
            
        if employee_id and profileImg:

            isExist = JobUsers.objects.filter(employee_code = employee_id).values('id', 'employee_code','employee_name','userProfileImage','is_logged')
            if isExist.exists():
                
                if file_url:
                    upload_image = file_from_url(profileImg, USER_PROFILE_FILE_LOCATION, USER_PROFILE_UPLOAD_PATH)
                else:
                    upload_image = file_upload(profileImg, USER_PROFILE_FILE_LOCATION, USER_PROFILE_UPLOAD_PATH) 
                
                if upload_image==False:
                    return Response({
                        'status' : False,
                        'detail' : 'The image url or file not downloadable.'
                    })
                
                # ~ userData = JobUsers.objects.get(employee_code=employee_id)    
                try:
                    file_json = dict()

                    file_json['fileURL']  = settings.BASE_URL+upload_image['upload_url']
                    file_json['fileHash'] = upload_image['hash']
                    file_json['fileSize'] = upload_image['size']
                    
                    isExist.update(userProfileImage=file_json, is_logged=True, updatedAt=timezones())
                    # ~ userData.save()

                    return Response({
                        'status' : True,
                        'detail' : 'Profile updated successfully',
                        'profile_data' : isExist[0],
                        'image' : file_json
                        
                    })
                except:
                # ~ # raise exception or error message
                    return Response({
                        'status' : False,
                        'detail' : 'Profile not updated'
                    })
            else:
                return Response({
                    'status' : False,
                    'detail' : 'User not exist with provided id.'
                })
        else:
            return Response({
                'status' : False,
                'detail' : 'Employee ID and profile image are mandatory'
            })

class AwardedUsers(GenericAPIView):
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
            employee_code=request.data.get('employee_id')
            user=JobUsers.objects.filter(employee_code=employee_code).values('id','employee_name','brand_id')
            brand_id=user[0].get('brand_id')
            result=StarOfTheMonth.objects.filter(brand_id=brand_id).values('id','title','user__id','user__userProfileImage','store__name','store__store_id')
            return Response({'status':True,'result':result})

class LeadershipBoard(GenericAPIView):
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
            winners=list(JobUsers.objects.filter().values('id','employee_code','employee_name','userProfileImage','user_point').order_by('-user_point'))[0:3]
            runners=list(JobUsers.objects.filter().values('id','employee_code','employee_name','userProfileImage','user_point').order_by('-user_point'))[3:]
            res={'status':True,'winners':winners,'runners':runners}
            return Response(res)

class PersonalLeadershipBoard(GenericAPIView):
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
            employee_code=request.data.get('employee_id')
            info=''
            level=''
            next_level=''
            User=JobUsers.objects.filter(employee_code=employee_code).values('id','employee_code','employee_name','userProfileImage','user_point')
            user_point=User[0].get('user_point')
            if user_point < 300:
                points_away=300-user_point
                level=None
                next_level=str(300-user_point)+' points needed more to unlock silver level'
                info='Congratulations!!! You have '+str(user_point)+' points due to your active contribution to Americana - KFC social community. Your active participation here keeps the people around you as cheerful and in high-spirits. Keep on contributing and spreading the happiness. You are now just '+str(points_away)+' points away from unlocking the Silver level.'
            elif (user_point >= 300) & (user_point < 500):
                points_away=500-user_point
                level='You are at Silver Level'
                next_level=str(500-user_point)+' points needed more to unlock gold level'
                info='Congratulations!!! You have been awarded Silver medal, as you have reached '+str(user_point)+' points due to your active contribution to Americana - KFC social community. Your active participation here keeps the people around you as cheerful and in high-spirits. Keep on contributing and spreading the happiness. You are now just '+str(points_away)+' points away from unlocking the Gold level.'
            elif (user_point >= 500) & (user_point < 1000):
                points_away=1000-user_point
                level='You are at Gold Level'
                next_level=str(1000-user_point)+' points needed more to unlock platinum level'
                info='Congratulations!!! You have been awarded Gold medal, as you have reached '+str(user_point)+' points due to your active contribution to Americana - KFC social community. Your active participation here keeps the people around you as cheerful and in high-spirits. Keep on contributing and spreading the happiness. You are now just '+str(points_away)+' points away from unlocking the Platinum level.'
            elif (user_point >= 1000):
                level='You are at Platinum Level'
                next_level=None
                info='Congratulations!!! You have been awarded Platinum medal, as you have reached '+str(user_point)+' points due to your active contribution to Americana - KFC social community. Your active participation here keeps the people around you as cheerful and in high-spirits. Keep on contributing and spreading the happiness.'
            res={'status':True,'userdetail':User[0],'info':info,'level':level,'next_level':next_level}
            return Response(res)    

class validatePhoneSendOTP(APIView):
    
    # authentication_classes = (TokenAuthentication,) 


    def post(self, request, *args, **kwargs):
        # destination1 = Employee.objects.all()
        # serializer = EmployeeSerializer(destination1, many=True)
        # kay = send_otp(999999)
        employee_id = request.data.get('employee_code')
        market = request.data.get('market')
        dob = request.data.get('dob')
        
        if employee_id:
            employee_id = str(employee_id)
           
            # user = CustomUser.objects.all()
            # serializer = CustomUserSerializer(user, many=True)
            # return Response(serializer.data)
            
            # CustomUser.objects.filter(employee_id=video_id).update(foo=video)

            user = JobUsers.objects.filter(employee_code__iexact=employee_id)
            
            if user.exists():
               
                userPhone = user[0].phone
                otp = send_otp(userPhone)
                user_data = JobUsers.objects.filter(phone=userPhone).values('id', 'employee_id','date_of_birth','first_name','middle_name','last_name','email','gender','user_id','store_id','sekret_key','user_type','start_date','term_date','primary_brand','multi_brand','work_phone','home_phone','fax','country','concept','bmu','record_type','job_role','franchise_id','department','manager_id', 'vender', 'gpn', 'is_staff', 'is_active', 'dateOfBirth', 'userProfileImage', 'userDescription')

                # saveuserdata.save() # this will update only
                # saveuserdata = CustomUser.objects.get(phone=userPhone)
                # saveuserdata.userDescription = 'If your idea of a 7 course meal is bucket of KFC '

                if otp:
                    otp = str(otp)
                    count = 0
                    old = PhoneOTP.objects.filter(phone__iexact = userPhone)
                    if old.exists():
                        count = old.first().count

                        # saveuserdata = CustomUser.objects.get(phone=userPhone)
                        # saveuserdata.first_name = 'Sobhan'
                        # saveuserdata.middle_name = 'Kumar'
                        # saveuserdata.last_name = 'Ray'
                        # saveuserdata.gender = 'M'
                        # saveuserdata.user_id = 12345
                        # saveuserdata.store_id = 2222222
                        # saveuserdata.sekret_key = 'N0518'
                        # saveuserdata.user_type = 'YRI-Corporate'
                        # saveuserdata.start_date = '2013-03-18'
                        # saveuserdata.term_date = '2013-03-18'
                        # saveuserdata.primary_brand = 'KFC'
                        # saveuserdata.multi_brand = 'K'
                        # saveuserdata.work_phone = '01244898992'
                        # saveuserdata.job_role = 'RGM'
                        # saveuserdata.franchise_id = 'DIPL'
                        # saveuserdata.department = 'Operations'
                        # saveuserdata.gpn = '1004142830'
                        # saveuserdata.save() # this will update only


                        t = PhoneOTP.objects.get(phone=userPhone)
                        t.count = count + 1
                        t.otp = otp
                        t.save() # this will update only
                    
                        # old.first().count = count + 1
                        # old.first().otp = otp
                        # old.first().save()
                    
                    else:
                        count = count + 1
            
                        PhoneOTP.objects.create(
                            phone =  userPhone, 
                            otp =   otp,
                            count = count
        
                            )
                    if count > 100:
                        return Response({
                            'status' : False, 
                            'detail' : 'Maximum otp limits reached. Kindly support our customer care or try with different number'
                        })
                    
                    
                else:
                    return Response({
                                'status': 'False', 'detail' : "OTP sending error. Please try after some time."
                            })
                # serializer = CustomUserSerializer()
                # serializer = CustomUser.objects.get(phone=userPhone)
                # user_data = serializer
                return Response({
                    'status': True, 
                    'detail': 'Otp has been sent successfully.', 
                    'data': otp, 
                    'profile_data' : user_data,
                    'phone': userPhone
                })
                # return Response({'status': False, 'detail': 'Phone Number already exists','data':serializer.data})
            else:
                return Response({'status': False, 'detail': 'Emoloyee id not exists'})
        else:
            return Response({
                'status': 'False', 'detail' : "I haven't received any Emoloyee id. Please do a POST request."
            })
                # data = request.data
                # mobile = data.get('mobile','')
                # return Response(mobile)

class ValidateOTP(APIView):
    '''
    If you have received otp, post a request with phone and that otp and you will be redirected to go further
    '''
    
    def post(self, request, *args, **kwargs):

        phone = request.data.get('phone', False)
        password = request.data.get('password', False)
        otp_sent   = request.data.get('otp', False)
        otp_sent = '1990-'+otp_sent[2:]+'-'+otp_sent[:2]
        
        
        if phone and otp_sent:
            old = JobUsers.objects.filter(phone__iexact = phone)
            # ~ old = CustomUser.objects.filter(user_id = str(user_id))
            print(old.query)
            if old.exists():
                old = old.first()
                otp = old.date_of_birth
                # ~ phone = old.phone
                # ~ print(aa)
                if str(otp) == str(otp_sent):
                    # old.logged = True
                    # old.save()
                    # ~ old.delete()

                    # user = old
                    # login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                    # account = get_account_from_hash(hash)
                    # if not account.is_active:
                    #     account.activate()
                    #     account.save()
                    #     user = account.user
                    #     login(request, user)


                    user = authenticate(phone=phone,password=password)
                    # login(request, user)

                    payload = {
                            'id': user.id,
                            'phone': user.phone,
                        }
                    # encoded_jwt = {'token' : jwt.encode(payload, 'SECRET_KEY') }
                    encoded_jwt = jwt.encode(payload, 'SECRET_KEY')
                    # email_obj.update(token=encoded_jwt['token'])
                    # return Response(encoded_jwt)
                    # isLogged = CustomUser.objects.get(phone=phone)
                    isLoggedStatus =False
                    isLogged = JobUsers.objects.filter(phone=phone).values('is_logged')
                    if isLogged.exists():
                        isLoggedStatus = isLogged[0]['is_logged']

                    # serializer = CustomUserSerializer(1)
                    # user_data = serializer.data
                    user_data = JobUsers.objects.filter(phone = phone).values('id', 'employee_id','phone','first_name','middle_name','last_name','email','gender','user_id','store_id','sekret_key','user_type','start_date','term_date','primary_brand','multi_brand','work_phone','home_phone','fax','country','concept','bmu','record_type','job_role','franchise_id','department','manager_id', 'vender', 'gpn', 'is_staff', 'is_active', 'dateOfBirth', 'userProfileImage', 'userDescription')

                    return Response({
                        'status' : True, 
                        'detail' : 'OTP matched, kindly proceed to add profile information',
                        'token' : encoded_jwt,
                        'isLoggedStatus' : isLoggedStatus,
                        'profile_data' : user_data[0],
                        # ~ 'aa' : aa
                    })
                else:
                    return Response({
                        'status' : False, 
                        'detail' : 'OTP incorrect, please try again'
                    })
            else:
                return Response({
                    'status' : False,
                    'aa' : phone,
                    'detail' : 'Phone not recognised. Kindly request a new otp witone not recognised. Kindly request a new otp with this number'
                })


        else:
            return Response({
                'status' : 'False',
                'detail' : 'Either phone or otp was not recieved in Post request'
            })

class GetOtherUserProfile(APIView):
    '''
    If you have received otp, post a request with phone and that otp and you will be redirected to go further
    '''
    authentication_classes = (TokenAuthentication,) 

    def post(self, request, *args, **kwargs):
        # employee_id = request.query_params.get('employee_id')
        user_id = request.data.get('user_id', False)

        if user_id:
            user_data = JobUsers.objects.filter(id = user_id).values('id', 'job_role__name', 'employee_id','phone','first_name','middle_name','last_name','email','gender','user_id','store_id','sekret_key','user_type','start_date','term_date','primary_brand','multi_brand','work_phone','home_phone','fax','country','concept','bmu','record_type','job_role','franchise_id','department','manager_id', 'vender', 'gpn', 'user_point', 'is_staff', 'is_active', 'dateOfBirth', 'userProfileImage', 'userDescription')
            if user_data.exists():
                user_detail = user_data[0]
                user_points = get_user_points(user_detail['id'], user_detail['user_point'])
                user_badge = get_user_badge(user_points)
                user_profile_data = user_detail 

                user_profile_data['user_badge'] = user_badge 
                user_profile_data['user_point'] = user_points 

                user_recognition = StarOfTheMonth.objects.filter(user_id=user_detail['id']).values('id', 'user_id' , 'title', 'award_lebel', 'selected_date', 'created_at', 'updated_at').order_by('-selected_date')
                post_cat = [2,3]
                special_posts = Posts.objects.filter(post_category__in = post_cat,user_id=user_detail['id']).values('id', 'user_id__first_name', 'user_id__middle_name', 'user_id__last_name', 'user_id__userProfileImage', 'user_id_id' ,'post_type', 'title', 'description', 'post_file', 'height', 'width', 'post_image', 'post_category__name', 'file_type', 'is_entity', 'status', 'verified_at', 'reactions','like_count', 'comment_count', 'created_at', 'updated_at').order_by('-id')
                # ~ print(special_posts.query)
               
                return Response({
                    'status' : True, 
                    'profile_data' : user_profile_data,
                    'special_posts' : special_posts,
                    'user_recognition' : user_recognition,

                })
            else:
                return Response({
                    'status' : 'False',
                    'detail' : 'Incorrect User ID'
                })

        else:
            return Response({
                'status' : 'False',
                'detail' : 'User ID is required'
            })


class userList(GenericAPIView):
    '''
    user List API
    '''
    authentication_classes = (TokenAuthentication,) 
    pagination_class = PageNumberPagination
    def get(self, request):

        if(request.method=="GET"):
            keyword = request.GET.get('keyword', False)
            if keyword:
                user_data = JobUsers.objects.filter(Q(email__icontains = keyword) | Q(first_name__icontains = keyword) | Q(last_name__icontains = keyword)).values('id','user_id','email','first_name','job_role','last_name','userProfileImage').distinct()
                if user_data.exists():
                    return Response({'status' : True, 'data' : user_data})
                else:
                    return Response({'status' : False, 'detail' : 'Data not exists'})
            else:
                return Response({'status' : False, 'detail' : 'Keyword is required'})
                

class AddUserBirthday(APIView):
    '''
    Add today birthday users in Post table
    '''
    # authentication_classes = (TokenAuthentication,) 
    def get(self, request, *args, **kwargs):

        saveuserdata = JobUsers.objects.filter()
        for noti in saveuserdata:
            noti.job_role = 1
            noti.save()
            
        my_cron_job()
        return Response({'status' : False, 'detail' : 'No Awarded users available'})

class AddUserworkanniversary(APIView):
    '''
    Add today birthday users in Post table
    '''
    # authentication_classes = (TokenAuthentication,) 
    def get(self, request, *args, **kwargs):
        add_user_work_anniversary()
        return Response({'status' : False, 'detail' : 'No Awarded users available'})
             

class WishUserBirthday(APIView):
    '''
    Wish User Birthday API
    '''
    def post(self, request, *args, **kwargs):
        if(request.method=="POST"):
           
            user_id = request.data.get('user_id', False)
            option_name = request.data.get('option_name', False)
            
            save_serialize = WishUserBirthdaySerializer(data=request.data)
            if save_serialize.is_valid(raise_exception=True):
                save_serialize.save()
                return Response(save_serialize.data, status=status.HTTP_201_CREATED)
            else:
                return Response({
                'status' : False,
                'detail' : 'HTTP_400_BAD_REQUEST'
                })
        else:
            return Response("", status=404)




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



class user_upload (LoginRequiredMixin, UpdateView):
    # declaring template
    # ~ template = "profile_upload.html"
    data = JobUsers.objects.all()
    
    # prompt is a context variable that can have different values depending on their context
    prompt = {
        'order': 'Order of the CSV should beCSV should name, email, address, phone, profile',
        'profiles': data    
              }
      
    # GET request returns the value of the data with the specified key.
    # ~ if request.method == "GET":
        # ~ return render(request, template, prompt)
    def post(self,request , *args, **kwargs):
       
        csv_file = request.FILES['file']
        # let's check if it is a csv file
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'THIS IS NOT A CSV FILE')
            return redirect(reverse('users:users'))
   
        df = pd.read_csv(csv_file)
        dataframe =  ['USERID','FIRSTNAME','MIDDLENAME','LASTNAME','DATE_OF_BIRTH','SECRETKEY','EMAIL','USER_TYPE','STARTDATE','TERMDATE','STATUS','PRIMARY_BRAND','MULTI_BRAND','WORK_PHONE','CELL_PHONE','HOME_PHONE','FAX','COUNTRY','CONCEPT','STOREID','BMU','RECORD_TYPE','JOBROLE','FRANCHISEID','DEPARTMENT','REQUESTOR_MAIL','MANAGER_ID','EMPLOYEEID','VENDOR','GPN','Name', 'Email', 'Phone' ,'Employee Id']
        column =   list(df.columns.values) 
        error_list = '' 
        count = 0
        for i in column :
            if not i in dataframe:
                count+=1
                error_list = error_list+' '+i+','
        if count!=0:
            messages.error(request, '{} column name is wrong. it must be column name like {} format.'.format(error_list,dataframe))
            return redirect(reverse('users:users'))
        
        
        job_roles   = JobRoles.objects.filter(status=True, is_deleted=False)
        
        job_role_id = {}
        for job_role_data in job_roles:
            job_role_id[job_role_data.name] = job_role_data.id
        
        print('job_role',job_role_id)
        for i in range(0,df.shape[0]):
            if df.iloc[i]['USERID'] and df.iloc[i]['JOBROLE'] and df.iloc[i]['FRANCHISEID']:
                
                dateOfBirth           = df.iloc[i]['DATE_OF_BIRTH'] 
                dateOfBirth           = dateOfBirth.split('/') 
                if str(df.iloc[i]['STARTDATE'])!= 'nan':
                    start_date            = df.iloc[i]['STARTDATE'] 
                    start_date            = start_date.split('/') 
                    start_date            = start_date[2]+'-'+start_date[0]+'-'+start_date[1]
                else:
                    start_date = ''
                        
                if str(df.iloc[i]['TERMDATE']) != 'nan':
                    term_date             = df.iloc[i]['TERMDATE'] 
                    term_date             = term_date.split('/') 
                    term_date             = term_date[2]+'-'+term_date[0]+'-'+term_date[1] 
                else:
                    term_date = ''
                
                user_id               = df.iloc[i]['USERID']
                first_name            = df.iloc[i]['FIRSTNAME']
                middle_name           = df.iloc[i]['MIDDLENAME']
                last_name             = df.iloc[i]['LASTNAME']
                dateOfBirth           = '1990-'+dateOfBirth[0]+'-'+dateOfBirth[1]
                secretkey             = df.iloc[i]['SECRETKEY']
                email                 = df.iloc[i]['EMAIL']
                user_type             = df.iloc[i]['USER_TYPE']
                start_date            = start_date
                term_date             = term_date
                status                = True if df.iloc[i]['STATUS'] == "Active" else False 
                primary_brand         = df.iloc[i]['PRIMARY_BRAND']
                multi_brand           = df.iloc[i]['MULTI_BRAND']
                work_phone            = df.iloc[i]['WORK_PHONE']
                phone                 = df.iloc[i]['CELL_PHONE']
                home_phone            = df.iloc[i]['HOME_PHONE']
                fax                   = df.iloc[i]['FAX']
                country               = df.iloc[i]['COUNTRY']
                concept               = df.iloc[i]['CONCEPT']
                store_id              = df.iloc[i]['STOREID']
                bmu                   = df.iloc[i]['BMU']
                record_type           = df.iloc[i]['RECORD_TYPE']
                # ~ job_role              = job_role_id.get(df.iloc[i]['JOBROLE'])
                job_role              = job_role_id[df.iloc[i]['JOBROLE']]
                franchise_id          = df.iloc[i]['FRANCHISEID']
                department            = df.iloc[i]['DEPARTMENT']
                requister_mail        = df.iloc[i]['REQUESTOR_MAIL']
                manager_id            = df.iloc[i]['MANAGER_ID']
                employee_id           = df.iloc[i]['EMPLOYEEID']
                vender                = df.iloc[i]['VENDOR']
                gpn                   = df.iloc[i]['GPN']
              
               
                if str(first_name)=='nan':
                    first_name = ''
                if str(email)=='nan':
                    email = ''
                if str(phone)=='nan':
                    phone = ''
                if str(employee_id)=='nan':
                    employee_id = ''
 
                try:
                    with transaction.atomic():                                
                        user_insert, created = JobUsers.objects.update_or_create(user_id  = df.iloc[i]['USERID'] ,first_name  = df.iloc[i]['FIRSTNAME'] ,middle_name  = df.iloc[i]['MIDDLENAME'],last_name=df.iloc[i]['LASTNAME'] ,dateOfBirth  = dateOfBirth,secretkey    =df.iloc[i]['SECRETKEY'] ,email  = df.iloc[i]['EMAIL'] ,user_type=df.iloc[i]['USER_TYPE'] ,start_date  = start_date  ,term_date  = term_date ,status  = status ,primary_brand  =df.iloc[i]['PRIMARY_BRAND'],multi_brand = df.iloc[i]['MULTI_BRAND']  ,work_phone  =df.iloc[i]['WORK_PHONE'],phone =df.iloc[i]['CELL_PHONE']   ,home_phone =df.iloc[i]['HOME_PHONE'] ,fax  = df.iloc[i]['FAX']   ,country  =df.iloc[i]['COUNTRY'] ,concept  =df.iloc[i]['CONCEPT']  ,store_id   =df.iloc[i]['STOREID'] ,bmu  = df.iloc[i]['BMU']  ,record_type  =df.iloc[i]['RECORD_TYPE'],job_role_id  =job_role ,franchise_id  =df.iloc[i]['FRANCHISEID'],department = df.iloc[i]['DEPARTMENT']   ,requister_mail  =df.iloc[i]['REQUESTOR_MAIL'] ,manager_id   = df.iloc[i]['MANAGER_ID'] ,employee_id  =df.iloc[i]['EMPLOYEEID'] ,vender  = df.iloc[i]['VENDOR']  ,gpn  =df.iloc[i]['GPN'],)
                        if created: 
                            print('The object was created')
                        else:
                            print('The object was updated')
                        created_id = user_insert.id
                        # ~ createdAt=timezones()
                        job_content = dict()
                        if created_id:
                            job_content['first_name']     = first_name
                            job_content['email']          = email
                            job_content['phone']          = phone
                            job_content['employee_id']    = employee_id
                            # ~ job_create('device-enrollement', job_content, created_id, '0', created_by, get_client_ip(self.request))
                except IntegrityError:
                    pass
        # ~ csv_string = defected_df.to_csv(r'/kfcEmpEngagementApp/kfcEmpEngagementApp/media/errors-csv/DefectedDevice.csv')
        # ~ if not defected_df.empty:
            # ~ data = {'data' : 0,'link':'https://kiosq.in/media/DefectedDevice.csv'}
        # ~ else:
            # ~ data = {'data' : 1,'link':''}    
                    
        return redirect(reverse('users:users'))            
                    
        
