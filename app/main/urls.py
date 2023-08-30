from django.urls import path

from .views import index, create_expense, incomes, edit_income, expenses, edit_expense, delete_expense

urlpatterns = [
    path('', index, name='index'),
    path('create-expense/', create_expense, name='create_expense'),
    path('incomes/', incomes, name='incomes'),
    path('income/edit', edit_income, name='edit_income'),
    path('expenses/', expenses, name='expenses'),
    path('expense/edit/<int:id>', edit_expense, name='edit_expense'),
    path('expense/delete/<int:id>', delete_expense, name='delete_expense')
    
]
