from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/users/", include("apps.users.urls")),
    path("api/properties/", include("apps.properties.urls")),
    path("api/search/", include("apps.search.urls")),
    path("api/ai-analysis/", include("apps.ai_analysis.urls")),
    path("", TemplateView.as_view(template_name="index.html")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
