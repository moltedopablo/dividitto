from django.urls import path

from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('expenses/', ExpenseListView.as_view(), name='expenses'),
    path('expenses/create', CreateExpenseView.as_view(), name='create_expense'),
    path('expenses/edit/<int:id>', EditExpenseView.as_view(), name='edit_expense'),
    path('expenses/delete/<int:id>', DeleteExpenseView.as_view(), name='delete_expense'),
    path('expenses/search', SearchExpenseView.as_view(), name='search_expenses'),
    path('expenses/page/<int:page>', ExpenseRowsView.as_view(), name='expenses_page'),
    path('expenses/settle', SettleExpenseView.as_view(), name='settle'),
    path('incomes/', incomes, name='incomes'),
    path('income/edit', edit_income, name='edit_income'),
]
