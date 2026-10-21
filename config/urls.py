from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

admin.site.site_header = "Blog – David Botcholi"
admin.site.site_title = "Blog admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("blog.urls")),
    # Médias servis par Django (suffisant pour un petit blog ;
    # voir le README pour un stockage persistant en production).
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
