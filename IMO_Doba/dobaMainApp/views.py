from django.shortcuts import render
from django.http import HttpResponse
from .models import Document
from django.http import JsonResponse
from .parseDoc import update_data
from django.shortcuts import get_object_or_404, redirect

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
    error_message = None
    start_date = None
    queryset = None
    end_date = None

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
    
    return render(request, 'dobaMainPage/repgeny.html', {'queryset':queryset})


def download_document(request, document_id):
    # Retrieve the document object from the database
    document = get_object_or_404(Document, pk=document_id)

    # Get the file content from the document object
    file_content = document.file_content

    # Create HTTP response for file download
    response = HttpResponse(file_content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{document.document_name}"'

    return response

def rename_doc(request, document_id):
    documents = get_object_or_404(Document, pk=document_id)
    context = {'document': documents}

    if request.method == 'POST':
        new_name = request.POST.get('new_name')

        if new_name: 
            documents.document_name = new_name
            documents.save()
    return render(request, 'dobaMainPage/rename_doc.html', context)

def delete_doc(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        document.delete()
    
    return redirect(request, 'dobaMainPage/dbview.html', {'documents': document})


