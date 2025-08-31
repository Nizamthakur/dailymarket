from django.urls import path
from . import views
urlpatterns = [
    path('user/register/', views.registration_view, name='registration_view'),
    path('user/login/', views.login_view, name='user_login'),
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('user/profile/', views.user_profile, name='user_profile'),
    path('user/logout/', views.user_logout, name='user_logout'),
    path('vendor/register/', views.vendor_registration_view, name='vendor_registration'),
    path('vendor/withdraw-request/', views.create_withdraw_request, name='create_withdraw_request'),
]
