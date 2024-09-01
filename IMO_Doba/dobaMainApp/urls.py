from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path('dbview/', views.doc_update, name='doc_update'), 
    path('dbview/<int:document_id>/', views.doc_update, name='doc_update'),
    path('download/<int:document_id>/', views.download_document, name='download_document'),
    path('rename/<int:document_id>/', views.rename_doc, name='rename_doc'),
    path('delete/<int:document_id>/', views.delete_doc, name='delete_doc'),
    path('search/', views.search_data, name='search_data'),
    path("repgen/", views.rep_gen, name = 'rep_gen'),
    path('export_csv/', views.export_csv, name='export_csv'),
    path('view_document/<int:document_id>/',views.view_document, name='view_document')
]


