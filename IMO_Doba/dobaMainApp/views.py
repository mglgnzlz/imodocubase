from django.shortcuts import render
from django.http import HttpResponse
from .models import Document

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def doc_update(request):
    # Fetch data from the database or perform any other operations
    documents = Document.objects.all()  # Example: Fetch all documents from the database

    # Pass data to the template
    context = {
        'documents': documents,  # Pass the documents queryset to the template
    }

    # Render the template
    return render(request, "frontpage.html", context)