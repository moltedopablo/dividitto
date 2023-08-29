from django.shortcuts import render
from django.shortcuts import render

from .forms import ExpenseForm, IncomeForm
from .models import Expense, Income
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required


def get_net_total(user):
    total_positive = Expense.objects.filter(user=user).aggregate(
        total_amount=Coalesce(Sum('net_value'), 0.0))['total_amount']
    total_negative = Expense.objects.exclude(
        user=user).aggregate(total_amount=Coalesce(Sum('net_value'), 0.0))['total_amount']
    return float(total_positive) - float(total_negative)


@login_required
def index(request):
    return render(request, 'index.html', {
        'expenses': Expense.objects.all(),
        'incomes': Income.objects.all(),
        'expenses_count': Expense.objects.count(),
        'users': User.objects.all(),
        'net_total': get_net_total(request.user),
    })


@login_required
def create_expense(request):
    form = ExpenseForm(request.POST or None)
    if form.is_valid():
        form.instance.user = User.objects.get(id=request.POST.get('user'))
        expense = form.save()
        expense.net_value = float(expense.value) * 0.5
        expense.save()
    return render(request, 'expense_list.html', {
        'expenses': Expense.objects.all(),
        'expenses_count': Expense.objects.count(),
        'net_total': get_net_total(request.user),
    })


@login_required
def income(request):
    return render(request, 'income.html', {
        'editing': False,
        'incomes': Income.objects.all()})


@login_required
def income_edit(request):
    if request.method == 'POST':
        incomes = {(key.split('-')[1], float(value)) for key,
                   value in request.POST.items() if key.startswith('income-')}
        total_income = sum([float(value) for (_, value) in incomes])
        for (user_id, value) in incomes:
            Income.objects.update_or_create(
                month=request.POST.get('month'),
                year=request.POST.get('year'),
                user=User.objects.get(id=user_id),
                defaults={
                    'percentage': value*100/total_income,
                    'value': value
                })
        return render(request, 'income.html', {
            'editing': False,
            'incomes': Income.objects.all()})
    else:
        return render(request, 'income.html', {
            'editing': True,
            'users': User.objects.all(),
            'incomes': Income.objects.all()})
