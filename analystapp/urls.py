from django.urls import path
from . import views

urlpatterns = [

    # =========================
    # AUTHENTICATION
    # =========================

    path(
        '',
        views.signup,
        name='signup'
    ),

    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

    path(
        'forgot-password/',
        views.forgot_password,
        name='forgot_password'
    ),

    path(
        'verify-otp/',
        views.verify_otp,
        name='verify_otp'
    ),

    path(
        'change-password/',
        views.change_password,
        name='change_password'
    ),

    # =========================
    # HOME
    # =========================

    path(
        'home/',
        views.home,
        name='home'
    ),

    # =========================
    # DATA CLEANING
    # =========================

    path(
        'clean/',
        views.clean_data,
        name='clean'
    ),

    # =========================
    # VISUALIZATION
    # =========================

    path(
        'visualize/',
        views.visualize,
        name='visualize'
    ),

    # =========================
    # PREDICTION
    # =========================

    path(
        'predict/',
        views.predict_page,
        name='predict'
    ),

]