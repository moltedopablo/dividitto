from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Expense(models.Model):
    date = models.DateField()
    title = models.CharField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.FloatField(
        validators=[MinValueValidator(0.1)], blank=True, null=True)
    is_settle = models.BooleanField(default=False)
    net_value = models.FloatField(
        validators=[MinValueValidator(0.1)], blank=True, null=True)

    def __str__(self):
        return self.title

    def calculate_net_value(self):
        income = Income.objects.filter(
            user=self.user, month=self.date.month, year=self.date.year).first()
        if self.value:
            if income:
                self.net_value = float(
                    self.value) * (100 - float(income.percentage)) / 100
            else:
                self.net_value = float(self.value) * 0.5

    class Meta:
        ordering = ['-date', '-id']


class Income(models.Model):
    month = models.IntegerField()
    year = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.FloatField(validators=[MinValueValidator(0.1)])
    percentage = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['month', 'year', 'user'], name='income_pk')
        ]
        ordering = ['-year', '-month', '-user']
