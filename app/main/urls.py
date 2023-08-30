from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('create-expense/', create_expense, name='create_expense'),
    path('incomes/', incomes, name='incomes'),
    path('income/edit', edit_income, name='edit_income'),
    path('expenses/', expenses, name='expenses'),
    path('expenses/edit/<int:id>', edit_expense, name='edit_expense'),
    path('expenses/delete/<int:id>', delete_expense, name='delete_expense'),
    path('expenses/search', search_expenses, name='search_expenses'),
    path('settle', settle, name='settle'),
]
