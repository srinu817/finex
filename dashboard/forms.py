from django import forms
from .models import Loan,Income,Expense

class LoanForm(forms.ModelForm):

    class Meta:
        model = Loan
        fields = "__all__"
# class IncomeForm(forms.ModelForm):
#     class Meta:
#         model = Income
#         fields = "__all__"

