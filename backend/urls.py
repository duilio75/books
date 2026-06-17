from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from api.views import CreateUserView, basic_page_detail
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", TemplateView.as_view(template_name="partials/home.html"), name="home"),
    path("admin/", admin.site.urls),
    path("api/user/register/", CreateUserView.as_view(), name="register"),
    path("api/token/", TokenObtainPairView.as_view(), name="get_token"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include("api.urls")),
    path("tinymce/", include("tinymce.urls")),
    # Catch-all: render a BasicPage by its url_alias, e.g. /prima-pagina-test/
    # Must stay LAST so it doesn't shadow admin/, api/, tinymce/, etc.
    path("<slug:url_alias>/", basic_page_detail, name="basic-page-detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)