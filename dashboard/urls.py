from django.urls import path
from . import views

urlpatterns = [

    # 🔐 AUTH
    path('login/', views.login_view, name="login"),
    path('signup/', views.signup_view, name="signup"),
    path('logout/', views.logout_view, name="logout"),

    # 🏠 DASHBOARD
    path('', views.dashboard_view, name="dashboard"),

    # 💸 EXPENSES
    path('expenses/', views.expenses_view, name="expenses"),
    path('delete-expense/<int:id>/', views.delete_expense, name='delete_expense'),

    # 💰 INCOME
    path('income/', views.income_view, name="income"),
    path('delete-income/<int:id>/', views.delete_income, name='delete_income'),

    # 🏦 LOANS
    path('loans/', views.loans_view, name="loans"),
    path('add-loan/', views.add_loan, name="add_loan"),
    path('loan-paid/<int:loan_id>/', views.mark_paid, name="mark_paid"),
    path('delete-loan/<int:id>/', views.delete_loan, name='delete_loan'),

    # 📊 REPORTS
    path('reports/', views.reports, name='reports'),

    # 👤 PROFILE & SETTINGS
    path('profile/', views.profile_view, name="profile"),
    path('settings/', views.settings_view, name="settings"),
    path('delete-account/', views.delete_account, name="delete_account"),
    path('otp-login/', views.otp_login, name='otp_login'),
path('verify-otp/', views.verify_otp, name='verify_otp'),
]