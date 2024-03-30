from django.shortcuts import render
from django.http import HttpResponse
from .models import Document
from django.http import JsonResponse
from .parseDoc import update_data

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def doc_update(request):
    # Fetch data from the database or perform any other operations
    update_data(request)
    documents = Document.objects.all()  # Example: Fetch all documents from the database
    


    # Render the template
    return render(request, "frontpage.html", {'documents': documents})

