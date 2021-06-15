from django.urls import path, include
from django.conf.urls import url
from . import views
from rest_framework import routers
from .serializers import *
# from .models import *
from rest_framework.urlpatterns import format_suffix_patterns


app_name = 'host'
urlpatterns = [
    url('BookingHost/', views.BookingHost.as_view()),
    url('EditHostProfile/', views.EditProfile.as_view()),
    url('testzb/',views.testzb, name="testzb"),
    path('testz/',views.testz, name="murl"),
    url('HostProfile/', views.Profile.as_view()),
    url('AllAppointments/', views.HostAppointmentList.as_view()),
    url('ChargerAppointments/', views.ChargerAppointmentList.as_view()
        ),
    url('MyEarning/', views.MyEarning.as_view()),
    url('AddCharger/', views.AddCharger.as_view()),
    url('EditCharger/', views.EditCharger.as_view()),
    url('AddSocketToCharget/', views.AddSocket.as_view()),
    url('AddNearby/', views.AddNearby.as_view()),
    url('EditNearby/', views.EditNearby.as_view()),
    url('AddPhotosToCharget/', views.AddPhoto.as_view()),
    url('EditSocketToCharget/', views.EditSocket.as_view()),
    url('DeletePhotosToCharget/', views.EditPhoto.as_view()),
    url('CheckReferal/', views.Referal.as_view()),
    #     # OTP
    url('SendOtp/', views.ValidatePhoneSendOTP.as_view()),
    url('VerifyOtp/', views.ValidateOTP.as_view()),
    url('Logout/', views.LogOut.as_view()),
    url('Notification/', views.HostNotificationList.as_view()),
    url('ChargerDetail/', views.ChargerDetail.as_view(), name="nurl"),
    url('Sockets/', views.Sockets.as_view()),
    url('CreditType/', views.CreditTypeView.as_view()),
    url('UpdateHostCredit/', views.UpdateHostCredit.as_view()),
    url('TotalChargerEarning/', views.TotalChargerEarning.as_view()),
    

]
urlpatterns = format_suffix_patterns(urlpatterns)
