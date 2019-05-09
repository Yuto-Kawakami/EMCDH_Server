"""MCDH URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls import url, include
from rest_framework import routers
from handbook import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'healths', views.HealthSet)
router.register(r'pregnancies', views.PregnancySet)
router.register(r'children', views.ChildSet)
router.register(r'gpacs', views.GPACSet)
router.register(r'consultationRecords', views.ConsultationRecordSet)
router.register(r'locations', views.LocationSet)
router.register(r'addresses', views.AddressSet)
router.register(r'accessControl', views.AccessControlSet)

urlpatterns = [
    path('user_summary/', views.UserSummary.as_view()),
    path('predict/', views.PredictAccessControl.as_view()),
    path('admin/', admin.site.urls),
    url(r'^', include(router.urls)),
]
