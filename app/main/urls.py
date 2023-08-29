from django.urls import path

from .views import index, create_expense, incomes, income_edit, expenses

urlpatterns = [
    path('', index, name='index'),
    path('create-expense/', create_expense, name='create-expense'),
    path('incomes/', incomes, name='incomes'),
    path('income/edit', income_edit, name='income_edit'),
    path('expenses/', expenses, name='expenses')
]
