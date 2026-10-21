import django_filters

from .models import Post


class PostFilter(django_filters.FilterSet):
    tag = django_filters.CharFilter(field_name="tags__slug", distinct=True)

    class Meta:
        model = Post
        fields = ["tag"]
