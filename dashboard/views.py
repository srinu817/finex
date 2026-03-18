from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from django.conf import settings
from django.core.mail import send_mail

from .models import Expense, Income, Loan
from .forms import LoanForm

import calendar


# 🔥 COMMON MAIL FUNCTION
def send_user_mail(user, subject, message):
    if user.email:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=True,
        )


# ========================= AUTH ========================= #

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")

        # 🔥 email login support
        try:
            user_obj = User.objects.get(email=username)
            username = user_obj.username
        except User.DoesNotExist:
            pass

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # 🔥 Remember Me Logic
            if not remember_me:
                request.session.set_expiry(0)  # logout on browser close
            else:
                request.session.set_expiry(1209600)  # 2 weeks

            return redirect("/dashboard/")
        else:
            return render(request, "dashboard/login.html", {"error": "Invalid credentials"})

    return render(request, "dashboard/login.html")

from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import render, redirect

from django.contrib import messages

def signup_view(request):
    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # 🔥 validation
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists ❌")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered ❌")
            return redirect("signup")

        try:
            # ✅ create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # ✅ auto login
            login(request, user)

            # 📧 send mail (SAFE)
            send_user_mail(user, "Welcome 🎉", "Your account created successfully!")

            messages.success(request, "Account created successfully 🎉")

            return redirect("/dashboard/")

        except Exception as e:
            print("SIGNUP ERROR:", e)
            messages.error(request, "Something went wrong. Try again ❌")
            return redirect("signup")

    return render(request, "dashboard/signup.html")


def logout_view(request):
    logout(request)
    return redirect("/login/")


# ========================= DASHBOARD ========================= #

@login_required
def dashboard_view(request):

    total_income = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_loan = Loan.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0

    wallet = total_income - total_expense - total_loan

    return render(request, "dashboard/dashboard.html", {
        "total_income": total_income,
        "total_expense": total_expense,
        "total_loan": total_loan,
        "wallet": wallet
    })


# ========================= EXPENSE ========================= #

@login_required
def expenses_view(request):

    if request.method == "POST":
        expense = Expense.objects.create(
            user=request.user,
            amount=request.POST["amount"],
            category=request.POST["category"],
            date=request.POST["date"]
        )

        send_user_mail(
            request.user,
            "Expense Added",
            f"₹{expense.amount} added under {expense.category}"
        )

        return redirect("expenses")

    expenses = Expense.objects.filter(user=request.user)
    return render(request, "dashboard/expenses.html", {"expenses": expenses})


@login_required
def delete_expense(request, id):
    exp = get_object_or_404(Expense, id=id, user=request.user)

    send_user_mail(
        request.user,
        "Expense Deleted",
        f"Deleted ₹{exp.amount} from {exp.category}"
    )

    exp.delete()
    return redirect("expenses")


# ========================= INCOME ========================= #

@login_required
def income_view(request):

    if request.method == "POST":
        income = Income.objects.create(
            user=request.user,
            amount=request.POST["amount"],
            source=request.POST["source"],
            date=request.POST["date"]
        )

        send_user_mail(
            request.user,
            "Income Added",
            f"₹{income.amount} added from {income.source}"
        )

        return redirect("income")

    incomes = Income.objects.filter(user=request.user)
    return render(request, "dashboard/income.html", {"incomes": incomes})


@login_required
def delete_income(request, id):
    inc = get_object_or_404(Income, id=id, user=request.user)

    send_user_mail(
        request.user,
        "Income Deleted",
        f"Deleted ₹{inc.amount} from {inc.source}"
    )

    inc.delete()
    return redirect("income")


# ========================= LOANS ========================= #

@login_required
def loans_view(request):
    loans = Loan.objects.filter(user=request.user)
    return render(request, "dashboard/loans.html", {"loans": loans})


@login_required
def add_loan(request):
    form = LoanForm(request.POST or None)

    if form.is_valid():
        loan = form.save(commit=False)
        loan.user = request.user
        loan.save()

        send_user_mail(
            request.user,
            "Loan Added",
            f"Loan ₹{loan.amount} added"
        )

        return redirect("loans")

    return render(request, "dashboard/add_loan.html", {"form": form})


@login_required
def delete_loan(request, id):
    loan = get_object_or_404(Loan, id=id, user=request.user)

    send_user_mail(
        request.user,
        "Loan Deleted",
        f"Deleted loan ₹{loan.amount}"
    )

    loan.delete()
    return redirect("loans")


@login_required
def mark_paid(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id, user=request.user)
    loan.status = "Paid"
    loan.save()

    send_user_mail(
        request.user,
        "Loan Paid",
        f"Loan ₹{loan.amount} marked as Paid"
    )

    return redirect("loans")


# ========================= REPORTS ========================= #

@login_required
def reports(request):

    monthly_expenses = list(
        Expense.objects.filter(user=request.user)
        .annotate(month=ExtractMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    monthly_income = list(
        Income.objects.filter(user=request.user)
        .annotate(month=ExtractMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    for item in monthly_expenses:
        item['month_name'] = calendar.month_abbr[item['month']]

    income_dict = {i['month']: i['total'] for i in monthly_income}

    for item in monthly_expenses:
        item['income'] = income_dict.get(item['month'], 0)

    total_income = sum(income_dict.values())
    total_expense = sum(i['total'] for i in monthly_expenses)
    wallet = total_income - total_expense

    # 📧 report mail
    if request.method == "POST":
        send_user_mail(
            request.user,
            "Monthly Report",
            f"Income: ₹{total_income}\nExpense: ₹{total_expense}\nWallet: ₹{wallet}"
        )

    return render(request, "dashboard/reports.html", {
        "monthly_expenses": monthly_expenses,
        "total_income": total_income,
        "total_expense": total_expense,
        "total_loan": 0,
        "wallet": wallet
    })
@login_required
def profile_view(request):

    if request.method == "POST":
        user = request.user

        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.save()

        send_user_mail(
            user,
            "Profile Updated",
            "Your profile details were updated successfully"
        )

        return redirect("profile")

    return render(request, "dashboard/profile.html")

@login_required
def settings_view(request):

    if request.method == "POST":
        password = request.POST.get("password")

        if password:
            user = request.user
            user.set_password(password)
            user.save()

            send_user_mail(
                user,
                "Password Changed",
                "Your password has been updated"
            )

            return redirect("/login/")

    return render(request, "dashboard/settings.html")
@login_required
def delete_account(request):

    user = request.user

    send_user_mail(
        user,
        "Account Deleted",
        "Your account has been removed successfully"
    )

    user.delete()
    return redirect("/signup/")
    
import random
from .models import OTP


def otp_login(request):

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "dashboard/otp.html", {"error": "User not found"})

        otp = str(random.randint(100000, 999999))

        OTP.objects.create(user=user, otp=otp)

        send_user_mail(user, "Your OTP", f"Your OTP is {otp}")

        return render(request, "dashboard/verify_otp.html", {"email": email})

    return render(request, "dashboard/login.html")
def verify_otp(request):

    if request.method == "POST":

        email = request.POST.get("email")
        otp_input = request.POST.get("otp")

        user = User.objects.get(email=email)
        otp_obj = OTP.objects.filter(user=user).last()

        if otp_obj and otp_obj.otp == otp_input:
            login(request, user)
            return redirect("/dashboard/")
        else:
            return render(request, "dashboard/verify_otp.html", {
                "error": "Invalid OTP",
                "email": email
            })

    return redirect("login")