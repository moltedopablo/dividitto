import datetime
from django.shortcuts import render

from .forms import ExpenseForm
from .models import Expense, Income
from .utils import get_month_name, get_current_month_year
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

EXPENSES_PAGE_SIZE = 30


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


def get_expenses_and_page(page):
    expense_list = Expense.objects.select_related('user').all()
    paginator = Paginator(expense_list, EXPENSES_PAGE_SIZE)
    page_obj = paginator.get_page(page)
    return (page_obj.object_list, page_obj.next_page_number)


@login_required
def index(request):
    (month, year) = get_current_month_year()
    (expenses, page) = get_expenses_and_page(1)
    return render(request, 'index.html', {
        'expenses': expenses,
        'page': page,
        'users': User.objects.all(),
        'incomes': Income.objects.filter(month=month, year=year),
        'net_total': get_net_total(request.user),
    })


@login_required
def expenses(request):
    (month, year) = get_current_month_year()
    (expenses, page) = get_expenses_and_page(1)
    return render(request, 'expenses.html', {
        'expenses': expenses,
        'page': page,
        'users': User.objects.all(),
        'incomes': Income.objects.filter(month=month, year=year),
        'net_total': get_net_total(request.user),
    })


def expenses_page(request, page):
    (expenses, page) = get_expenses_and_page(page)
    return render(request, 'expense_rows.html', {
        'expenses': expenses,
        'page': page,
        'users': User.objects.all(),
        'net_total': get_net_total(request.user),
    })


def set_expense_net_value(expense):
    income = Income.objects.filter(
        user=expense.user, month=expense.date.month, year=expense.date.year).first()
    if income:
        expense.net_value = float(
            expense.value) * (100 - float(income.percentage)) / 100
    else:
        expense.net_value = float(expense.value) * 0.5
    expense.save()


@login_required
def create_expense(request):
    form = ExpenseForm(request.POST or None)
    if form.is_valid():
        form.instance.user = User.objects.get(id=request.POST.get('user'))
        expense = form.save()
        set_expense_net_value(expense)
    (expenses, page) = get_expenses_and_page(1)
    return render(request, 'expense_list.html', {
        'expenses': expenses,
        'page': page,
        'net_total': get_net_total(request.user),
    })


@login_required
def delete_expense(request, id):
    expense = Expense.objects.get(id=id)
    expense.delete()
    (expenses, page) = get_expenses_and_page(1)
    return render(request, 'expense_list.html', {
        'expenses': expenses,
        'page': page,
        'net_total': get_net_total(request.user),
    })


@login_required
def edit_expense(request, id):
    if request.method == 'POST':
        expense = Expense.objects.get(id=id)
        if expense.is_settle:
            raise Exception("Cannot edit a settled expense")

        form = ExpenseForm(request.POST or None, instance=expense)
        if form.is_valid():
            form.instance.user = User.objects.get(id=request.POST.get('user'))
            expense = form.save()
            set_expense_net_value(expense)

        (expenses, page) = get_expenses_and_page(1)
        return render(request, 'expense_list.html', {
            'expenses': expenses,
            'page': page,
            'net_total': get_net_total(request.user),
        })
    else:
        expense = Expense.objects.get(id=id)
        return render(request, 'expense_edit.html', {
            'users': User.objects.all(),
            'expense': expense,
        })


@login_required
def incomes(request):
    date_params = get_date_params(
        request.GET.get('month'), request.GET.get('year'))
    return render(request, 'incomes.html', {
        'editing': False,
        'users': User.objects.all(),
        'incomes': Income.objects.filter(month=date_params['month'], year=date_params['year']),
        **date_params
    })


def recalculate_expenses_net_vale(month, year):
    expenses = Expense.objects.filter(date__month=month, date__year=year)
    with transaction.atomic():
        for expense in expenses:
            if not expense.is_settle:
                set_expense_net_value(expense)
                expense.save()


@login_required
def edit_income(request):
    if request.method == 'POST':
        (month, year) = (int(request.POST.get('month')), int(request.POST.get('year')))

        incomes = {(key.split('-')[1], float(value)) for key,
                   value in request.POST.items() if key.startswith('income-')}
        total_income = sum([float(value) for (_, value) in incomes])

        for (user_id, value) in incomes:
            Income.objects.update_or_create(
                month=month,
                year=year,
                user=User.objects.get(id=user_id),
                defaults={
                    'percentage': value*100/total_income,
                    'value': value
                })

        recalculate_expenses_net_vale(month, year)

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


@login_required
def settle(request):
    net_total = get_net_total(request.user)
    if net_total < 0:
        user = request.user
    elif net_total > 0:
        user = User.objects.exclude(id=request.user.id).first()
    else:
        raise Exception("Cannot settle if net total is 0")

    Expense.objects.create(
        title="💵 Saldado",
        value=None,
        net_value=abs(net_total),
        user=user,
        is_settle=True,
        date=datetime.datetime.now())
    
    (expenses, page) = get_expenses_and_page(1)
    return render(request, 'expense_list.html', {
        'expenses': expenses,
        'page': page,
        'net_total': get_net_total(request.user),
    })


@login_required
def search_expenses(request):
    search_str = request.POST.get('search')
    expenses = Expense.objects.filter(title__icontains=search_str)

    return render(request, 'expense_table.html', {
        'expenses': expenses,
        'net_total': get_net_total(request.user),
    })
