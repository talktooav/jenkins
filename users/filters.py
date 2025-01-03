import django_filters
from .models import User

class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(label='Usernames')

    class Meta:
        model = User
        fields = {
            'username': ['exact', 'contains'],
            'email': ['exact', 'contains'],
        }

    # def my_custom_filter(self, queryset, name, value):
    #     return queryset.filter(**{
    #         name: value,
    #     })