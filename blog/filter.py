from django_filters import rest_framework as filters

from .models import Post

class PostFilter(filters.FilterSet):
    category = filters.RangeFilter()
    tags = filters.RangeFilter()

    class Meta:
        model = Post
        fields = ['category', 'tags']