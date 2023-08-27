from django.shortcuts import render
from django.shortcuts import render

from .forms import ExpenseForm
from .models import Expense
from django.contrib.auth.models import User
from django.views.generic.list import ListView


def index(request):
    return render(request, 'index.html')


def create_expense(request):
    form = ExpenseForm(request.POST or None)
    if form.is_valid():
        form.instance.user = User.objects.get(id=request.POST.get('user'))
        form.save()
        form = ExpenseForm()

    expenses = Expense.objects.all()
    return render(request, 'expense_list.html', {'expenses': expenses, 'expenses_count': Expense.objects.count()})


def expenses(request):
    expenses = Expense.objects.all()
    users = User.objects.all()
    return render(request, 'expenses.html', {'expenses': expenses, 'expenses_count': Expense.objects.count(), 'users': users})
