from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Expense(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    amount = models.FloatField()

    category = models.CharField(max_length=100)

    date = models.DateField()

    notes = models.TextField(blank=True)


class Income(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    amount = models.FloatField()

    source = models.CharField(max_length=100)

    date = models.DateField()

    notes = models.TextField(blank=True)



class Loan(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        person = models.CharField(max_length=100)
        amount = models.DecimalField(max_digits=10, decimal_places=2)
        date = models.DateField()

        status = models.CharField(
        max_length=10,
        choices=[
            ('Pending', 'Pending'),
            ('Paid', 'Paid')
        ],
        default='Pending'
    )
        def __str__(self):
         return self.person