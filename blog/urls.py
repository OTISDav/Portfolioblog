from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PostViewSet, SitemapView, TagViewSet

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")
router.register("tags", TagViewSet, basename="tag")

urlpatterns = [
    path("sitemap/", SitemapView.as_view(), name="sitemap"),
    path("", include(router.urls)),
]
