from django.db import models
from django import forms
import os

class Document(models.Model):
    document_name = models.CharField(max_length=100)
    document_type = models.CharField(max_length=50)
    supplier = models.CharField(max_length=100)
    date = models.DateField()
    file_content = models.BinaryField(default=b'')
    file_path = models.CharField(max_length=512, default='')
    orig_docName = models.CharField(max_length=255, blank=True)
    remarks = models.TextField(blank=True, null=True)
    po_number = models.CharField(max_length=255, null=True, blank=True)

    STATUS_CHOICES = [
        ('In','In'),
        ('Out','Out'),
    ]
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default = '')
    
    
    
    def extract_file_type(self):
        """Extracts document type from the filename and converts it to uppercase."""
        parts = self.document_name.split('_')
        if len(parts) > 1:
            return parts[0].upper()
        return 'UNKNOWN'

    @property
    def file_type(self):
        return self.extract_file_type()
    
    def save(self, *args, **kwargs):
        
        if not self.orig_docName:
            self.orig_docName = self.file_path
        super().save(*args, **kwargs)
        
        
    def __str__(self):
       return self.document_name
    
