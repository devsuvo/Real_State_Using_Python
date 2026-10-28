from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Crystal Bay Estates"
admin.site.site_title = "Crystal Bay Admin"
admin.site.index_title = "Website Control Panel"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("dashboard.urls")),
    path("properties/", include("properties.urls")),
    path("blog/", include("blog.urls")),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "core.views.page_not_found"
