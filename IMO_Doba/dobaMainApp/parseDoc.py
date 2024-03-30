import os
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from .models import Document

def parse_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        parseIndex = filename.split('_')
        if len(parseIndex) >= 4:
            document_name = parseIndex[0]
            document_type = parseIndex[1]
            supplier = parseIndex[2]
            date_str = parseIndex[3].split('.')[0]
            date = datetime.strptime(date_str, '%Y-%m-%d').date()

            document = Document(
                document_name=document_name,
                document_type=document_type,
                supplier=supplier,
                date=date
            )

            document.save()


def update_data(request):
    # Specify the folder path where your PDF files are located
    folder_path = 'D:/SCHOOL/DOBA_WebApp/IMO_Doba/sample_DB'
    parse_folder(folder_path)
    print("function call")

