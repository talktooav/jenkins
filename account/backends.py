from rest_framework import status
from rest_framework import authentication, exceptions
from jobusers.models import JobUsers
from rest_framework.authentication import get_authorization_header, BaseAuthentication
from django.http import HttpResponse
import jwt


class TokenAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        auth_data = authentication.get_authorization_header(request)

        if not auth_data:
            msg = "token is required"
            raise exceptions.AuthenticationFailed(msg)

        prefix, token = auth_data.decode('utf-8').split(' ')

        try:
            # ~ payload = jwt.decode(token, 'SECRET_KEY') 
            payload = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])

            user = JobUsers.objects.get(employee_code=payload['e_code'])
            return (user, token)

        except jwt.DecodeError as identifier:
            raise exceptions.AuthenticationFailed(
                'Your token is invalid,login')
        except jwt.ExpiredSignatureError as identifier:
            raise exceptions.AuthenticationFailed(
                'Your token is expired,login')

        return super().authenticate(request)

class TokenAuthentication_old(BaseAuthentication):

    model = None

    def get_model(self):
        return JobUsers

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
      
        if not auth:
            msg = "token is required"
            raise exceptions.AuthenticationFailed(msg)

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1]
            if token=="null":
                msg = 'Null token not allowed'
                raise exceptions.AuthenticationFailed(msg)
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        # model = self.get_model()
        
        payload = jwt.decode(token, "SECRET_KEY")
        emp_code = payload['e_code']
        userid = payload['id']
        
        msg = {'Error': "Token mismatch",'status' :"401"}
        try:
            
            user = User.objects.get(
                email=emp_code,
                id=userid,
                is_active=True
            )
            # if not user.token == token:
            #     raise exceptions.AuthenticationFailed(msg)
               
        except jwt.ExpiredSignature or jwt.DecodeError or jwt.InvalidTokenError:
            return HttpResponse({'Error': "Token is invalid"}, status="403")
        except User.DoesNotExist:
            return HttpResponse({'Error': "Internal server error"}, status="500")

        return (user, token)

    def authenticate_header(self, request):
        return 'Token'
