from django import forms
from .models import Borrower

class BorrowerForm(forms.ModelForm):
    class Meta:
        model = Borrower
        fields = '__all__'