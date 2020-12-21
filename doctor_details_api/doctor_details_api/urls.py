"""doctor_details_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path

from base import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('doctor_search_vitals/', views.doctor_search, name="Vitals Doctor Search"),
    path('doctor_search_webmd/', views.doctor_search, name="WebMD Doctor Search"),
    path('doctor_profile_vitals/', views.profile_data, name="Vitals Doctor Profile"),
    path('doctor_profile_webmd/', views.profile_data, name="WebMD Doctor Profile"),
]
