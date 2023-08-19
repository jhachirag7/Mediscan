from django.urls import path,include
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register", views.RegistrationView.as_view(), name="register"),
    path("dropbox", views.dropbox, name="dropbox"),
    path("results", views.results, name="results"),
    path("history", views.history, name="history"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("payment", views.payment, name="payment"),
    path('validate-username', csrf_exempt(views.UsernameValidate.as_view()),
         name="validate-username"),
    path('validate-email', csrf_exempt(views.EmailValidate.as_view()),
         name="validate-email"),
    path('activate/<uid64>/<token>', views.EmailActivation.as_view(), name="activate"),
    path('login', views.LoginView.as_view(), name="login"),
    path('logout', views.LogoutView.as_view(), name="logout"),
    path('reset-password', csrf_exempt(views.ResetPassword.as_view()),
         name="reset-password"),
    path('pass-activate/<uid64>/<token>',
         csrf_exempt(views.PasswordConfirm.as_view()), name="pass-activate"),
    path('billing', csrf_exempt(views.billing.as_view()),
         name="bill"),
    path("order", views.Order, name="order"),

]
