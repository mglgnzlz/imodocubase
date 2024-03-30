from django.urls import path

from . import views

urlpatterns = [
    path("", views.doc_update, name='doc_update'),
]


