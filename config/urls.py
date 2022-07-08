"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
import django
from django.contrib import admin
from django.urls import path
from django.urls import include

from my_app.views import choose_file_view, file_upload_view, home_view, file_delete_view, dir_add_view

from django.contrib.auth import views as auth_views

from my_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include("django.contrib.auth.urls")),
    path('upload_file/', file_upload_view, name='upload_file'),
    path('dir_add/', dir_add_view, name='add_dir'),
    path('', home_view, name='home'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('ajax/delete', file_delete_view, name='delete_file'),
    path('ajax/choose', choose_file_view, name='choose_file'),
    path('ajax/run_frama', views.run_view, name='run_frama'),
    path('ajax/save_file', views.safe_file_view, name='save_file'),
]
