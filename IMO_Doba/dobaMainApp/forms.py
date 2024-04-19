from django import forms
from .models import Document


class RenameDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_name']