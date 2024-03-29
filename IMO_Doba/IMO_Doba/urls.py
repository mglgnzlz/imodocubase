
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("dobaMainApp/", include("dobaMainApp.urls")),
    path("admin/", admin.site.urls),
]