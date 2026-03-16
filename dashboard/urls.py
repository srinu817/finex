from django.urls import path
from .views import *
from . import views


urlpatterns = [

path('', dashboard_view, name="dashboard"),
path("add-loan/", views.add_loan, name="add_loan"),
path('login/', login_view, name="login"),
path('signup/', signup_view, name="signup"),
path('logout/', logout_view, name="logout"),
path("loan-paid/<int:loan_id>/", views.mark_paid, name="mark_paid"),
    path("loans/", views.loans_view, name="loans"),
    path("reports/", views.reports_view, name="reports"),
path("edit-loan/<int:id>/", views.edit_loan, name="edit_loan"),
path("delete-loan/<int:id>/", views.delete_loan, name="delete_loan"),

path('profile/', profile_view, name="profile"),
path('settings/', settings_view, name="settings"),

path('expenses/', expenses_view, name="expenses"),
path('income/', income_view, name="income"),

]