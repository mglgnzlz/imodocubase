import os
from django.shortcuts import render
from datetime import datetime
from django.http import HttpResponse
from .models import Document

def search_data(request):
    query = request.GET.get('query')
    
    if query:
        results = Document.objects.filter(title__icontains=query)
    else:
        results = []
    
    context = {
        'query':query,
        'results':results
    }

    return render(request, "dobaMainPage/searchPage.html", context)