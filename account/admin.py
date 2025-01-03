from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
#from .forms import CustomUserCreationForm, CustomUserChangeForm
#from .models import CustomUser,UserEntity,Posts,StarOfTheMonth,Moderation,Notification,PostCategory,JobRoles


class CustomUserAdmin(UserAdmin):
    #add_form = CustomUserCreationForm
    #form = CustomUserChangeForm
    #model = CustomUser
    list_display = ('email', 'first_name', 'phone','employee_id','is_superuser','is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('phone','job_role', 'user_id', 'email','first_name','middle_name','last_name','gender', 'entity_id','start_date','date_of_birth', 'password','userDescription')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'email', 'user_id', 'employee_id', 'first_name','middle_name','last_name', 'entity_id', 'job_role', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active')}
        ),
    )
    search_fields = ('phone',)
    ordering = ('email',)


#admin.site.register(CustomUser, CustomUserAdmin)

#admin.site.register(UserEntity)
#admin.site.register(Posts)
#admin.site.register(Moderation)
#admin.site.register(Notification)
#admin.site.register(PostCategory)
#admin.site.register(JobRoles)

class StarOfTheMonthAdmin(admin.ModelAdmin):
   
    list_display = ('user_id','title', 'award_lebel', 'selected_date', 'created_at',)
    list_per_page = 10

#admin.site.register(StarOfTheMonth, StarOfTheMonthAdmin)
