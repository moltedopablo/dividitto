from django.urls import path

from .views import index, create_expense, income, income_edit

urlpatterns = [
    path('', index, name='index'),
    path('create-expense/', create_expense, name='create-expense'),
    path('income/', income, name='income'),
    path('income/edit', income_edit, name='income_edit')
]
