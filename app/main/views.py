from django.shortcuts import render

from .forms import ExpenseForm
from .models import Expense, Income
from .utils import get_month_name, get_current_month_year
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required


def get_date_params(month, year):
    if month is None:
        month = get_current_month_year()[0]
    if year is None:
        year = get_current_month_year()[1]

    (month, year) = (int(month), int(year))
    (prev_month, prev_year) = (month - 1, year) if month > 1 else (12, year - 1)
    (next_month, next_year) = (month + 1, year) if month < 12 else (1, year + 1)
    return {
        'month': month,
        'year': year,
        'month_name': get_month_name(month),
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year, }


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
        'users': User.objects.all(),
        'net_total': get_net_total(request.user),
    })


@login_required
def expenses(request):
    return render(request, 'expenses.html', {
        'expenses': Expense.objects.all(),
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
        'net_total': get_net_total(request.user),
    })


@login_required
def incomes(request):
    date_params = get_date_params(
        request.GET.get('month'), request.GET.get('year'))
    return render(request, 'incomes.html', {
        'editing': False,
        'incomes': Income.objects.filter(month=date_params['month'], year=date_params['year']),
        **date_params
    })


@login_required
def income_edit(request):
    if request.method == 'POST':
        (month, year) = (int(request.POST.get('month')), int(request.POST.get('year')))
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
        return render(request, 'incomes.html', {
            'editing': False,
            'incomes': Income.objects.filter(month=month, year=year),
            **get_date_params(month, year)
        })
    else:
        (month, year) = (int(request.GET.get('month')), int(request.GET.get('year')))
        return render(request, 'incomes.html', {
            'editing': True,
            'users': User.objects.all(),
            'incomes': Income.objects.filter(month=month, year=year),
            **get_date_params(month, year)
        })
