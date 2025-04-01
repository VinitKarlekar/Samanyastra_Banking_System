"""
URL configuration for bankapplications project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from website import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Authentication Routes
    path('', views.login, name='login'),
    path('Register/', views.Register, name='register'),
    path('create_account/', views.create_account, name='create_account'),
    path('login_process/', views.login_process, name='login_process'),

    # Bank Information Routes
    path('bank_informations/', views.bank_informations, name='bank_informations'),
    path('save_bank_info/', views.save_bank_info, name='save_bank_info'),
    path("bank_login/", views.bank_login, name='bank_login'),
    path("bank_login_process/", views.bank_login_process, name='bank_login_process'),
    path("bank_details/", views.bank_details, name='bank_details'),
    path('view_balance/', views.view_balance, name='view_balance'),

    # Transaction Routes
    path("transfer_money/", views.transfer_money, name='transfer_money'),
    path("all_transactions/", views.all_transactions, name="all_transactions"),
    path("withdraw_money/", views.withdraw_money, name="withdraw_money"),

    # Profile Management
    path('profile_view/', views.profile_view, name='profile_view'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('update_profile/', views.update_profile, name='update_profile'),

    # Logout Routes
    path("acc_logout/", views.acc_logout, name='acc_logout'),
    path("dashboard_logout/", views.dashboard_logout, name='dashboard_logout'),

    # Dashboard & Messages
    path('Dashboard/', views.Dashboard, name='dashboard'),
    path('Messages/', views.Messages, name='messages'),
    path('get_messages/', views.get_messages, name='get_messages'),

    # Admin Panel
    path('admin/', admin.site.urls),
]

# Serve media files in development mode
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
