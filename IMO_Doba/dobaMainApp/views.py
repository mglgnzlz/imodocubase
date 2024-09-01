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
import xlsxwriter
import mimetypes
from django.conf import settings
from django.db.models import Count
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def doc_update(request, document_id = None):
    if document_id:
        document = Document.objects.get(id=document_id)
    # Fetch data from the database or perform any other operations
    update_data(request)
        
    print("Request GET data:", request.GET)
    print("Request POST data:", request.POST)
    
    try:
        if request.method == 'POST':
            document_id = request.POST.get('document_id')
            po_number = request.POST.get('po_number')
            remarks = request.POST.get('remarks')
            status = request.POST.get('status')
            
            document = Document.objects.get(id=document_id)
            if po_number:
                document.po_number = po_number
            if remarks:
                document.remarks = remarks
            if status:
                document.status = status 
            
            document.save()

            return redirect('doc_update')
        
        
        # Get request parameters
        sort_date = request.GET.get('sort-date', None)
        sort_supplier = request.GET.get('sort-supplier', None)

        # Base queryset
        documents = Document.objects.all()

        # Determine sorting order
        date_order = '-' if sort_date == 'descending' else ''
        supplier_order = '-' if sort_supplier == 'desc' else ''

        # Sort the queryset
        documents = documents.order_by(f'{date_order}date', f'{supplier_order}supplier')

        # Paginate the queryset
        num_paginator = Paginator(documents, 10)
        page = request.GET.get('page')

        documents = num_paginator.get_page(page)

        # Prepare context data
        context = {
            'documents': documents,
            'sort_date': sort_date,
            'sort_supplier': sort_supplier}

    except Exception as e:
        error_message = "An error occurred: " + str(e)
        context['error_message'] = error_message

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
            'time_period': time_period, }

    except Exception as e:
        error_message = "An error occurred: " + str(e)
        context['error_message'] = error_message

    return render(request, 'dobaMainPage/repgeny.html', context)


#def export_csv(request):

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
    queryset = queryset.order_by(f'{date_order}date', f'{supplier_order}supplier')

    # Group by company and document type
    company_dict = {}
    for document in queryset:
        company = document.supplier
        file_name = f'{document.extract_file_type()}_{company}_{document.date.strftime("%Y-%m-%d")}'
        if company not in company_dict:
            company_dict[company] = {'count': 0, 'files': []}
        company_dict[company]['count'] += 1
        company_dict[company]['files'].append(file_name)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    if start_date and end_date:
        file_name = f'REPORT_GENERATION_{start_date.strftime("%B_%d_%Y")}_to_{end_date.strftime("%B_%d_%Y")}.csv'
    else:
        file_name = 'REPORT_GENERATION_ALL_FILES.csv'

    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    writer = csv.writer(response)

    # Write headers
    headers = ['COMPANY NAME', 'FILE NAMES', '# OF TRANSACTIONS']
    writer.writerow(headers)

    # Write company data
    for company, data in company_dict.items():
        filenames = '\n'.join(data['files'])  # Join filenames with line breaks
        writer.writerow([company, filenames, data['count']])
        writer.writerow([''])  # Add a blank row for spacing

    # Add extra blank row for spacing between company data and summary
    writer.writerow([''])
    writer.writerow([''])

    # Write summary
    if start_date and end_date:
        date_range = f'DATE RANGE: {start_date.strftime("%m/%d/%Y")} - {end_date.strftime("%m/%d/%Y")}'
    else:
        date_range = 'DATE RANGE: ALL FILES'

    summary_row = [date_range]
    for company in company_dict.keys():
        summary_row.append(f'# OF TRANSACTIONS OF {company}')
    writer.writerow(summary_row)

    count_row = ['']
    for data in company_dict.values():
        count_row.append(data['count'])
    writer.writerow(count_row)

    return response
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
    queryset = queryset.order_by(f'{date_order}date', f'{supplier_order}supplier')

    # Group by company and document type
    company_dict = {}
    for document in queryset:
        company = document.supplier
        file_name = f'{document.extract_file_type()}_{company}_{document.date.strftime("%Y-%m-%d")}'
        if company not in company_dict:
            company_dict[company] = {'count': 0, 'files': []}
        company_dict[company]['count'] += 1
        company_dict[company]['files'].append({
            'file_name': file_name,
            'status': document.status,
            'remarks': document.remarks,
            'po_number': document.po_number
        })

    # Create an HttpResponse object with Excel content
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    if start_date and end_date:
        file_name = f'REPORT_GENERATION_{start_date.strftime("%B_%d_%Y")}_to_{end_date.strftime("%B_%d_%Y")}.xlsx'
    else:
        file_name = 'REPORT_GENERATION_ALL_FILES.xlsx'

    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    # Create an Excel workbook and worksheet
    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet()

    # Define cell formats
    wrap_format = workbook.add_format({'text_wrap': True})
    bold_format = workbook.add_format({'bold': True})
    
    # Write headers
    headers = ['SUPPLIER', '# OF DOCUMENTS', 'FILENAME', 'STATUS', 'REMARKS', 'PO NUMBER']
    worksheet.write_row('A1', headers, bold_format)

    row = 1
    # Write company data
    for company, data in company_dict.items():
        # Write the supplier and number of documents
        worksheet.write(row, 0, company, wrap_format)
        worksheet.write(row, 1, data['count'], wrap_format)
        row += 1
        # Write file details for the supplier
        for file_detail in data['files']:
            worksheet.write(row, 2, file_detail['file_name'], wrap_format)
            worksheet.write(row, 3, file_detail['status'], wrap_format)
            worksheet.write(row, 4, file_detail['remarks'], wrap_format)
            worksheet.write(row, 5, file_detail['po_number'], wrap_format)
            row += 1
        # Add extra blank row for separation
        row += 1

    # Write summary
    row += 2  # Add some space before the summary
    if start_date and end_date:
        date_range = f'DATE RANGE: {start_date.strftime("%m/%d/%Y")} - {end_date.strftime("%m/%d/%Y")}'
    else:
        date_range = 'DATE RANGE: ALL FILES'

    worksheet.write(row, 0, date_range, wrap_format)
    col = 1
    for company in company_dict.keys():
        worksheet.write(row, col, f'# OF TRANSACTIONS OF {company}', wrap_format)
        col += 1

    row += 1
    count_row = ['']
    for data in company_dict.values():
        count_row.append(data['count'])
    worksheet.write_row(row, 1, count_row, wrap_format)

    # Adjust column widths
    worksheet.set_column('A:A', 20)  # Supplier column width
    worksheet.set_column('B:B', 15)  # Document count column width
    worksheet.set_column('C:C', 40)  # Filename column width
    worksheet.set_column('D:D', 15)  # Status column width
    worksheet.set_column('E:E', 30)  # Remarks column width
    worksheet.set_column('F:F', 15)  # PO Number column width

    workbook.close()
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
            Q(document_name__icontains=query) |
            Q(po_number__icontains=query) |
            Q(remarks__icontains=query) |
            Q(status__icontains=query)).order_by('id')

        page = request.GET.get('page', 1)
        num_paginator = Paginator(results, 10)
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
    response['Content-Disposition'] = f'inline; filename="{document.document_name}"'
    return response
