from django.urls import path

from . import views

app_name = "monstrinhos"

urlpatterns = [
    path("", views.home, name="home"),
    path("novo/", views.cadastrar, name="cadastrar"),
    path("monstrinho/<int:pk>/", views.detalhe, name="detalhe"),
    path("monstrinho/<int:pk>/alimentar/", views.alimentar, name="alimentar"),
]
