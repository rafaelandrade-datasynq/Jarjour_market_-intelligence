from api.urls import api
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
    path("dashboard/", include("dashboard.urls")),
    path("exports/", include("exports.urls")),
]
