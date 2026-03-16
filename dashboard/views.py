from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .models import Expense, Income, Loan
from .forms import LoanForm


# LOGIN
def login_view(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("/")
        else:
            return render(request, "dashboard/login.html", {"error": "Invalid login"})

    return render(request, "dashboard/login.html")


# SIGNUP
def signup_view(request):

    if request.method == "POST":

        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        User.objects.create_user(username=username, email=email, password=password)

        return redirect("/login/")

    return render(request, "dashboard/signup.html")


# LOGOUT
def logout_view(request):
    logout(request)
    return redirect("/login/")


# DASHBOARD
@login_required
def dashboard_view(request):

    total_income = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_loan = Loan.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0

    wallet = total_income - total_expense - total_loan

    context = {
        "total_income": total_income,
        "total_expense": total_expense,
        "total_loan": total_loan,
        "wallet": wallet
    }

    return render(request, "dashboard/dashboard.html", context)


# PROFILE
@login_required
def profile_view(request):
    return render(request, "dashboard/profile.html")


# SETTINGS
@login_required
def settings_view(request):
    return render(request, "dashboard/settings.html")


# EXPENSE
@login_required
def expenses_view(request):

    if request.method == "POST":

        Expense.objects.create(
            user=request.user,
            amount=request.POST["amount"],
            category=request.POST["category"],
            date=request.POST["date"]
        )

    expenses = Expense.objects.filter(user=request.user)

    return render(request, "dashboard/expenses.html", {"expenses": expenses})


# INCOME
@login_required
def income_view(request):

    if request.method == "POST":

        Income.objects.create(
            user=request.user,
            amount=request.POST["amount"],
            source=request.POST["source"],
            date=request.POST["date"]
        )

    incomes = Income.objects.filter(user=request.user)

    return render(request, "dashboard/income.html", {"incomes": incomes})


# ADD LOAN
@login_required
def add_loan(request):

    form = LoanForm(request.POST or None)

    if form.is_valid():
        loan = form.save(commit=False)
        loan.user = request.user
        loan.save()

        return redirect("loans")

    return render(request, "dashboard/add_loan.html", {"form": form})


# LOANS PAGE
@login_required
def loans_view(request):

    loans = Loan.objects.filter(user=request.user)

    return render(request, "dashboard/loans.html", {"loans": loans})


# MARK LOAN PAID
@login_required
def mark_paid(request, loan_id):

    loan = get_object_or_404(Loan, id=loan_id, user=request.user)

    loan.status = "Paid"
    loan.save()

    return redirect("loans")


# REPORTS
@login_required
def reports_view(request):

    total_income = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_loan = Loan.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0

    wallet = total_income - total_expense - total_loan

    context = {
        "total_income": total_income,
        "total_expense": total_expense,
        "total_loan": total_loan,
        "wallet": wallet
    }

    return render(request, "dashboard/reports.html", context)

def edit_loan(request, id):
    loan = Loan.objects.get(id=id)

    if request.method == "POST":
        form = LoanForm(request.POST, instance=loan)
        if form.is_valid():
            form.save()
            return redirect("loans")

    else:
        form = LoanForm(instance=loan)

    return render(request, "dashboard/add_loan.html", {"form": form})


def delete_loan(request, id):
    loan = Loan.objects.get(id=id)
    loan.delete()
    return redirect("loans")