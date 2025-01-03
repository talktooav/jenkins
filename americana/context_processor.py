from users.models import User
from .utils import session_dict
from django.conf import settings

# use to get base url
def base_url(request):
    return {'base_url' : settings.BASE_URL}

# use for slug pass on every template
def subdomain_slug(request):
    user_slug    = False
    dict_session = session_dict(request)
    if dict_session:
        if 'auth_user_slug' in dict_session:
            user_slug = dict_session['auth_user_slug']
    return { 'subdomain_slug' : user_slug }


# use for pass enterprise list on every page in navbar.html                    
def all_brands(request):
    brand_list = dict()
    brand_list[0] = 'Global Admin'
    dict_session = session_dict(request)
    superuser = False
    if dict_session:
        user_id  = dict_session['_auth_user_id']
        brand_id = dict_session['auth_brand_id']
        if 'is_superuser' in dict_session:
            superuser = dict_session['is_superuser']

        if 'auth_user_role' in dict_session:
            user_role = dict_session['auth_user_role']
            user_type = dict_session['auth_user_type']
            # ~ if user_role == 'Enterprise':
            if user_type == 'brand':
                brand_users = User.objects.filter(id=user_id)
            elif user_type == 'sub-brand':
                brand_users = User.objects.filter(id=brand_id)
            elif superuser==True:
                brand_users = User.objects.filter(user_type='brand', is_deleted=0).order_by('id')
            else:
                brand_users = User.objects.filter(created_by=user_id, user_type='brand', is_deleted=0).order_by('id')
            if brand_users:
                for ent in brand_users:
                    brand_list[str(ent.id)] = ent.name
    return {'all_brands' : brand_list }
    
