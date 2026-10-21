from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import PostFilter
from .models import Post, Tag
from .serializers import PostDetailSerializer, PostListSerializer, TagSerializer


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    filterset_class = PostFilter
    search_fields = ("title", "excerpt", "content")

    def get_queryset(self):
        return Post.objects.filter(published=True).prefetch_related("tags")

    def get_serializer_class(self):
        return PostDetailSerializer if self.action == "retrieve" else PostListSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    lookup_field = "slug"


class SitemapView(APIView):
    """Slugs + dates de mise à jour des articles publiés (pour le sitemap du frontend)."""

    def get(self, request):
        posts = Post.objects.filter(published=True).values("slug", "updated_at")
        return Response(list(posts))
