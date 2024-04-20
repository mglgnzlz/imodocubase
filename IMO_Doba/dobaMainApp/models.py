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
    
    
    def save(self, *args, **kwargs):
        
        if not self.orig_docName:
            self.orig_docName = self.file_path
        super().save(*args, **kwargs)
        
        
    def __str__(self):
       return self.document_name
    
