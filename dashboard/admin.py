from django.contrib import admin

# Register your models here.
from .models import Expense, Income

admin.site.register(Expense)
admin.site.register(Income)