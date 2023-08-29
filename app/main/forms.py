from .models import Expense
from django import forms


class ExpenseForm(forms.ModelForm):
    class Meta:
        fields = ["title", "value", "date"]
        model = Expense

class IncomeForm(forms.Form):
    month = forms.IntegerField()
    year = forms.IntegerField()
    value = forms.FloatField()
    percentage = forms.FloatField()