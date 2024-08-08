from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, Http404
from .models import Document
from django.http import JsonResponse
from .parseDoc import update_data
from django.shortcuts import get_object_or_404, redirect
from .forms import RenameDocumentForm
from send2trash import send2trash
from django.core.paginator import Paginator
import os


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def doc_update(request):
    # Fetch data from the database or perform any other operations
    update_data(request)

    sort_date = request.GET.get('sort-date', None)
    sort_supplier = request.GET.get('sort-supplier', None)
    file_type = request.GET.getlist('file-type[]')

    # If no sorting or filtering parameters are provided, return all documents
    if not sort_date and not sort_supplier and not file_type:
        documents = Document.objects.all()
    else:
        # Determine the sorting order
        date_order = '-' if sort_date == 'descending' else ''
        supplier_order = '-' if sort_supplier == 'desc' else ''
        
        if not file_type:
            documents = Document.objects.all()
        elif 'MISC' in file_type:
            documents = Document.objects.exclude(document_type__in=['IAR', 'EPR'])
        else:
            documents = Document.objects.filter(document_type__in=file_type)
        
        
        documents = documents.order_by(f'{date_order}date', f'{supplier_order}supplier')
    
    # Set Up Pagination
    num_paginator = Paginator(documents, 10)  # Use the sorted and filtered documents
    page = request.GET.get('page')
    
    documents = num_paginator.get_page(page)
    
    
    context = {
        'documents': documents, 
        'file_type': file_type, 
        'sort_date': sort_date, 
        'sort_supplier': sort_supplier
    }
    
    return render(request, "dobaMainPage/dbview.html", context)


def home(request):

    # Scripts for HOME PAGE to Django Backend
    documents = Document.objects.all()

    return render(request, "dobaMainPage/home.html", {'documents': documents})


def translogs(request):

    # Scripts for TRANSMISSION LOGS to Django Backend

    return render(request, "dobaMainPage/translogs.html", {'documents': documents})



def rep_gen(request):
    error_message = None
    context = {}

    try:
        # Get request parameters
        sort_date = request.GET.get('sort-date', None)
        sort_supplier = request.GET.get('sort-supplier', None)
        file_type = request.GET.getlist('file-type')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Base queryset
        queryset = Document.objects.all()

        # Apply date range filter
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        # Apply file type filter
        if 'MISC' in file_type:
            queryset = queryset.exclude(document_type__in=['IAR', 'EPR'])
        else:
            queryset = queryset.filter(document_type__in=file_type)

        # Determine sorting order
        date_order = '-' if sort_date == 'descending' else ''
        supplier_order = '-' if sort_supplier == 'desc' else ''

        # Sort the queryset
        queryset = queryset.order_by(f'{date_order}date', f'{supplier_order}supplier')

        # Paginate the queryset
        paginator = Paginator(queryset, 10)  # Show 10 documents per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Prepare context data
        context = {
            'page_obj': page_obj,
            'sort_date': sort_date,
            'sort_supplier': sort_supplier,
            'file_type': file_type,
            'start_date': start_date,
            'end_date': end_date,
        }

    except Exception as e:
        error_message = "An error occurred: " + str(e)
        context['error_message'] = error_message

    return render(request, 'dobaMainPage/repgeny.html', context)

 

def download_document(request, document_id):
    # Retrieve the document object from the database
    document = get_object_or_404(Document, pk=document_id)

    # Get the file content from the document object
    file_path = document.file_path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(
                fh.read(), content_type='appication/octet-stream')
            response['Content-Disposition'] = 'inline; filename =' + \
                os.path.basename(file_path)
            return response
    raise Http404


def rename_doc(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    if request.method == 'POST':
        form = RenameDocumentForm(request.POST, instance=document)
        if form.is_valid():
            # Save the updated document name
            new_fileName = form.cleaned_data['document_name']

            base_filename = new_fileName.rsplit('(', 1)[0].strip()[:-4]

            # Count how many filenames start with the base filename
            existing_files_count = Document.objects.filter(
                document_name__startswith=base_filename).count()
            print(existing_files_count)
            # If a file with the same name exists, append a number to the file name
            if existing_files_count > 0:
                # If a file with the same name exists, keep incrementing the file count until a unique filename is found
                while True:
                    new_fileName = f"{
                        base_filename} ({existing_files_count}).pdf"
                    print(new_fileName)
                    if not Document.objects.filter(document_name=new_fileName).exists():
                        break
                    existing_files_count += 1

            old_filePath = document.file_path
            new_filePath = os.path.join(
                os.path.dirname(old_filePath), new_fileName)
            os.rename(old_filePath, new_filePath)
            document.file_path = new_filePath

            document.document_name = new_fileName
            document.save()

            original_document_id = document_id
            document.delete()

            update_data(request)
            return redirect('/dbview')  # Redirect to document detail page
    else:
        # Initialize the form with the document instance
        form = RenameDocumentForm(instance=document)

    return render(request, 'dobaMainPage/rename_doc.html', {'document': document, 'form': form})


def delete_doc(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    file_path = document.file_path

    if request.method == 'POST':
        try:
            print("Deleting " + file_path)
            send2trash(file_path)
            document.delete()
            return redirect('/dbview')

        except:
            HttpResponseNotFound(f"FILE '{file_path}' NOT FOUND")
            return redirect('/dbview')

    return render(request, 'dobaMainPage/delConf.html', {'document': document})


def search_data(request):
    query = request.GET.get("query")
    if query:

        results = Document.objects.filter(
            document_name__icontains=query).order_by('id')
        
        page = request.GET.get('page', 1)
        num_paginator = Paginator(results, 5)
        results = num_paginator.page(page)

        return render(request, "dobaMainPage/searchPage.html", {'query': query, 'results': results})

    else:
        return render(request, "dobaMainPage/searchPage.html")
