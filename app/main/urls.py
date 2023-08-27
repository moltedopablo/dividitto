from django.urls import path

from .views import expenses, index, create_expense

urlpatterns = [
    path('', index, name='index'),
    path('create-expense/', create_expense, name='create-expense'),
    path("expenses/", expenses, name='expense-list'),
]
