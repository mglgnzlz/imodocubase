from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("dbview/", views.doc_update, name ='doc_update'),
    path("translogs/", views.translogs, name='translogs'),
    path("repgen/", views.rep_gen, name = 'rep_gen'),
]


