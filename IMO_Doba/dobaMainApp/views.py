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
    return render(request, "dobaMainPage/dbview.html", {'documents': documents})

def home(request):

    documents = Document.objects.all

    return render(request, "dobaMainPage/home.html", {'documents':documents})

def translogs(request):
    documents = Document.objects.all

    return render(request, "dobaMainPage/translogs.html", {'documents':documents})

def rep_gen(request):
    documents = Document.objects.all
    try:

        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            # Perform query to retrieve data based on date range
            queryset = Document.objects.filter(date__range=[start_date, end_date])

            # Return response (render report template or return data as JSON/XML)
            return render(request, 'dobaMainPage/repgeny.html', {'queryset':queryset})

    except Exception as e:
            error_message = "An error occurred: " + str(e)
            return render(request, 'dobaMainPage/repgeny.html', {'error_message': error_message})
