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
import re
import csv
import mimetypes
from django.conf import settings
from django.db.models import Count
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def doc_update(request):
    # Fetch data from the database or perform any other operations
    update_data(request)

    sort_date = request.GET.get('sort-date', None)
    sort_supplier = request.GET.get('sort-supplier', None)
    file_type = request.GET.getlist('file-type[]')

    documents = Document.objects.all()
    date_order = '-' if sort_date == 'descending' else ''
    supplier_order = '-' if sort_supplier == 'desc' else ''

    documents = documents.order_by(f'{date_order}date', f'{
                                   supplier_order}supplier')
    
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
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        time_period = request.GET.get('time-period', 'all-files')

        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None

        # Base queryset
        queryset = Document.objects.all()

        # Apply date range filter based on time period
        if time_period and time_period != 'all-files':
            end_date = datetime.now().date()
            if time_period == 'last-month':
                start_date = end_date - timedelta(days=30)
            elif time_period == 'last-3-months':
                start_date = end_date - timedelta(days=90)
            elif time_period == 'last-6-months':
                start_date = end_date - timedelta(days=180)
            queryset = queryset.filter(date__range=[start_date, end_date])
        elif start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])


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
            'start_date': start_date_str,
            'end_date': end_date_str,
            'time_period': time_period,}

    except Exception as e:
        error_message = "An error occurred: " + str(e)
        context['error_message'] = error_message

    return render(request, 'dobaMainPage/repgeny.html', context)



def export_csv(request):
    sort_date = request.GET.get('sort-date', None)
    sort_supplier = request.GET.get('sort-supplier', None)
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    time_period = request.GET.get('time-period')

    # Parse dates
    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    # Base queryset
    queryset = Document.objects.all()

    # Apply date range filter based on time period
    if time_period and time_period != 'all-files':
        end_date = datetime.now().date()
        if time_period == 'last-month':
            start_date = end_date - timedelta(days=30)
        elif time_period == 'last-3-months':
            start_date = end_date - timedelta(days=90)
        elif time_period == 'last-6-months':
            start_date = end_date - timedelta(days=180)
        queryset = queryset.filter(date__range=[start_date, end_date])
    elif start_date and end_date:
        queryset = queryset.filter(date__range=[start_date, end_date])

    # Determine sorting order
    date_order = '-' if sort_date == 'descending' else ''
    supplier_order = '-' if sort_supplier == 'desc' else ''

    # Sort the queryset
    queryset = queryset.order_by(f'{date_order}date', f'{
                                 supplier_order}supplier')

    # Create a dictionary for document type counts
    # document_type_counts = queryset.values('document_name').annotate(
    #     document_type=Count('id')
    # ).order_by()

    document_type_count_dict = {}
    for document in queryset:
        doc_type = document.extract_file_type()
        if doc_type not in document_type_count_dict:
            document_type_count_dict[doc_type] = 0
        document_type_count_dict[doc_type] += 1

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')

    # Determine the file name based on the date range
    if start_date and end_date:
        file_name = f'REPORT_GENERATION_{start_date.strftime("%B_%d_%Y")}_to_{
            end_date.strftime("%B_%d_%Y")}.csv'
    else:
        file_name = 'REPORT_GENERATION_ALL_FILES.csv'

    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    writer = csv.writer(response)

    # Create headers
    headers = ['Document Type'] + \
        [f'Count of {doc_type}' for doc_type in document_type_count_dict.keys()]
    writer.writerow(headers)

    # Create a single row with the counts of each document type
    row = ['']  # Empty cell for 'Document Type'
    row += [count for count in document_type_count_dict.values()]
    writer.writerow(row)

    return response
 

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

            # Extract the base filename and the optional count part
            base_filename_match = re.match(
                r'^(.*?)( \(\d+\))?\.pdf$', new_fileName)
            if not base_filename_match:
                # If the filename does not match the expected pattern
                form.add_error(None, "Invalid filename format")
                return render(request, 'dobaMainPage/rename_doc.html', {'document': document, 'form': form})

            base_filename = base_filename_match.group(1).strip()
            optional_part = base_filename_match.group(2) or ""

            # Count how many filenames start with the base filename
            existing_files_count = Document.objects.filter(
                document_name__startswith=base_filename).count()

            # If a file with the same name exists, append a number to the file name
            if existing_files_count > 0:
                count = 1
                # If a file with the same name exists, keep incrementing the file count until a unique filename is found
                while True:
                    new_fileName = f"{base_filename} ({count}).pdf"
                    if not Document.objects.filter(document_name=new_fileName).exists():
                        break
                    count += 1
            else:
                new_fileName = f"{base_filename}.pdf"

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


def view_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    file_path = os.path.join(settings.MEDIA_ROOT, document.file_path)
    if not os.path.exists(file_path):
        raise Http404("File not found")

    with open(file_path, 'rb') as f:
        file_content = f.read()

    mime_type, _ = mimetypes.guess_type(document.document_name)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    response = HttpResponse(file_content, content_type=mime_type)
    response['Content-Disposition'] = f'inline; filename="{
        document.document_name}"'
    return response
