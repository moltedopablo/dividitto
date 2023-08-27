from .models import Expense
from django import forms


class ExpenseForm(forms.ModelForm):
    class Meta:
        fields = ["title", "value", "date"]
        model = Expense
