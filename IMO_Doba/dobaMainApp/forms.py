from django import forms
from django.core.validators import RegexValidator
from .models import Document


class RenameDocumentForm(forms.ModelForm):

    pattern = r'[A-Za-z0-9_ ]+_[A-Za-z0-9_ ]+_\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])(\ \(\d+\))?\.pdf$'

    document_name = forms.CharField(validators=[RegexValidator(
        regex=pattern, message="Invalid document name format")])

    class Meta:
        model = Document
        fields = ['document_name']
