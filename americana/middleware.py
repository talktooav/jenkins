from django.utils.deprecation import MiddlewareMixin
from .utils import session_dict
from django.http import Http404  


class CurrentSlugMiddleware(MiddlewareMixin):
    def process_request(self, request):
        pathh = request.path
        spl = pathh.split('/')
        dict_session = session_dict(request)
        
        if dict_session and request.user:
            user_slug = dict_session['auth_user_slug']
            if 'auth_brand_id' in dict_session:
                login_enterprise = dict_session['auth_brand_id']
                if int(login_enterprise) < 1:
                    if any(app in pathh for app in ['users', 'roles', 'logout', 'change-password', 'dashboard', 'login', 'media', 'moderation', 'userentity', 'jobuser', 'jobrole', 'postcategory', 'poll', 'post', 'reports', 'rewards', 'quiz', 'americana-store']):
                        pass
                    elif user_slug != spl[1]:
                        raise Http404
                    else:    
                        raise Http404
            # ~ if 'auth_user_slug' in dict_session:
                # ~ user_slug = dict_session['auth_user_slug']
                # ~ if any(app in pathh for app in ['users', 'roles', 'logout', 'change-password', 'dashboard', 'media', 'login']):
                    # ~ pass
                # ~ elif user_slug != spl[1]:
                    # ~ raise Http404
    
