import os
from datetime import datetime
from django.http import HttpResponse
from .models import Document

from datetime import datetime
from django.http import HttpResponse
from .models import Document
import os

def parse_folder(folder_path):
    for filename in os.listdir(folder_path):
        try:
            if filename.endswith('.pdf'):
                file_path = os.path.join(folder_path, filename)
                parseIndex = filename.split("_")
                if len(parseIndex) >= 3:
                    document_name = filename
                    document_type = parseIndex[0]
                    supplier = parseIndex[1]
                    date_str = parseIndex[2].split('.')[0]
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()

                    existing_document = Document.objects.filter(document_name=document_name, date=date).first()
                    if existing_document:
                        print(f"Document {document_name} already exists in the database. Skipping...")
                    else:
                        # Save the document to the database
                        document = Document(
                            document_name=filename,
                            document_type=document_type,
                            supplier=supplier,
                            date=date
                        )
                        document.save()
                        print(f"Document {document_name} saved to the database.")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

def update_data(request):
    folder_path = 'D:/SCHOOL/DOBA_WebApp/IMO_Doba/sample_DB'
    try:
        parse_folder(folder_path)
        print("function call " + folder_path)
        return HttpResponse("Data updated successfully")
    except Exception as e:
        print(f"Error updating data: {e}")
        return HttpResponse("An error occurred while updating data")
