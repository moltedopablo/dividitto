from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Expense(models.Model):
    date = models.DateField()
    title = models.CharField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2, validators=[
                                MinValueValidator(1)])

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-date', '-id']
