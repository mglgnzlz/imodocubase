from django.db import models

class Document(models.Model):
    document_name = models.CharField(max_length=100)
    document_type = models.CharField(max_length=50)
    supplier = models.CharField(max_length=100)
    date = models.DateField()
    file_content = models.BinaryField(default=b'')

    def __str__(self):
       return self.document_name