from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("monstrinhos.urls")),
]

admin.site.site_header = "Monstrinhos • Administração"
admin.site.site_title = "Monstrinhos"
admin.site.index_title = "Gerencie sua coleção"
