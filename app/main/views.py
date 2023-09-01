import datetime
from django.shortcuts import render

from .forms import ExpenseForm
from .models import Expense, Income
from .utils import get_current_month_year, get_date_params
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

EXPENSES_PAGE_SIZE = 30


@method_decorator(login_required, name="dispatch")
class ExpenseView(TemplateView):
    template_name = "index.html"

    def get_expenses_and_page(self, page):
        expense_list = Expense.objects.select_related('user').all()
        paginator = Paginator(expense_list, EXPENSES_PAGE_SIZE)
        page_obj = paginator.get_page(page)
        return (page_obj.object_list, page_obj.next_page_number)

    def get_net_total(self):
        user = self.request.user
        total_positive = Expense.objects.filter(
            user=user).aggregate(sum=Coalesce(Sum('net_value'), 0.0))
        total_negative = Expense.objects.exclude(
            user=user).aggregate(sum=Coalesce(Sum('net_value'), 0.0))
        return float(total_positive['sum']) - float(total_negative['sum'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        (expenses, page) = self.get_expenses_and_page(1)
        context['expenses'] = expenses
        context['page'] = page
        context['net_total'] = self.get_net_total()

        return context


class ExpenseListView(ExpenseView):
    template_name = "expenses.html"

    def get_context_data(self, **kwargs):
        (month, year) = get_current_month_year()
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        context['incomes'] = Income.objects.filter(month=month, year=year)

        return context


class IndexView(ExpenseListView):
    template_name = "index.html"


class ExpenseRowsView(ExpenseView):
    template_name = "expense_rows.html"

    def get_context_data(self, **kwargs):
        (expenses, page) = self.get_expenses_and_page(kwargs['page'])
        return {'expenses': expenses, 'page': page}


class CreateExpenseView(ExpenseView):
    template_name = "expense_list.html"

    def post(self, request, *args, **kwargs):
        form = ExpenseForm(request.POST or None)
        if form.is_valid():
            form.instance.user = User.objects.get(id=request.POST.get('user'))
            expense = form.save()
            expense.calculate_net_value()
            expense.save()
        return render(request, self.template_name, self.get_context_data())


class DeleteExpenseView(ExpenseView):
    template_name = "expense_list.html"

    def post(self, request, *args, **kwargs):
        expense = Expense.objects.get(id=kwargs['id'])
        expense.delete()
        return render(request, self.template_name, self.get_context_data())


class EditExpenseView(ExpenseView):
    template_name = "expense_edit.html"

    def post(self, request, *args, **kwargs):
        expense = Expense.objects.get(id=kwargs['id'])
        if expense.is_settle:
            raise Exception("Cannot edit a settled expense")

        form = ExpenseForm(request.POST or None, instance=expense)
        if form.is_valid():
            form.instance.user = User.objects.get(id=request.POST.get('user'))
            expense = form.save()
            expense.calculate_net_value()
            expense.save()
        return render(request, 'expense_list.html', self.get_context_data())

    def get(self, request, *args, **kwargs):
        expense = Expense.objects.get(id=kwargs['id'])
        return render(request, self.template_name, {
            'users': User.objects.all(),
            'expense': expense,
        })


class SettleExpenseView(ExpenseView):
    template_name = "expense_list.html"

    def post(self, request, *args, **kwargs):
        net_total = self.get_net_total()
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
        return render(request, self.template_name, self.get_context_data())


class SearchExpenseView(ExpenseView):
    template_name = "expense_table.html"

    def post(self, request, *args, **kwargs):
        seach_str = request.POST.get('search')
        expenses = Expense.objects.filter(title__icontains=seach_str)

        return render(request, self.template_name, {
            'expenses': expenses,
            'net_total': self.get_net_total(),
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
                expense.calculate_net_value()
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
