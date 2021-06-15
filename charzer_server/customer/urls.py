from django.urls import path, include
from django.conf.urls import url
from . import views
from rest_framework import routers
from .serializers import *
from .models import *
from rest_framework.urlpatterns import format_suffix_patterns


app_name = 'customer'
urlpatterns = [
    # Customer Api
    # # url('CustomerList/', views.CustomerViewSet.as_view()),

    # /customer/CustomerProfile/?customer_id=1&authkey=
    url('CustomerProfile/', views.Profile.as_view()),

    # /customer/ReferalCheck/?referalID=&customer_id=1&authkey=
    url('ReferalCheck/', views.Referal.as_view()),

    #     # Appointment APIS
    #     # /customer/AppointmentDetail/?app_ID=1&customer_id=1&authkey=
    url('AppointmentDetail/', views.GetAppointment.as_view()),
    url('AppointmentStatus/', views.ChangeStatusAppointment.as_view()),
    url('CreateAppointment/', views.CreateAppointment.as_view()),



    #     # /customer/AppointmentList/?customer_id=1&authkey=
    url('AppointmentList/', views.AppointmentList.as_view()),

    #     # charger APIS
    # /customer/ChargerDetail/?charger_id=1
    url('ChargerDetail/', views.ChargerDetail
        .as_view()),

    #     # Bookmark APIS
    #     # /customer/Bookmarks/?favourite_customer=1&customer_id=1&authkey=
    url('Bookmarks/', views.BookmarkList.as_view()),

    #     # /customer/EditBookmark/?favourite_ID=1&customer_id=1&authkey=
    url('EditBookmark/', views.EditBookmarkCharger.as_view()),

    #     # /customer/Bookmark/?favourite_ID=1&customer_id=1&authkey=
    url('Bookmark/', views.BookmarkCharger.as_view()),

    # Filter API
    # /customer/filter/?power=&socket=&amenities=&parking=&networks=&distance=&latitude=&longitude=&customer_id=1&authkey=
    url('filter/', views.Filter
        .as_view()),

    # OTP APIS
    url('SendOtp/', views.ValidatePhoneSendOTP.as_view()),
    url('VerifyOtp/', views.ValidateOTP.as_view()),
    url('Logout/', views.LogOut.as_view()),
    #     # Subscribe
    url('Subscribe/', views.Subscribe.as_view()),
    #     # Vehicle APIS
    # /customer/VehicleList/?customer_id=1&authkey=
    url('VehicleList/', views.VehicleList.as_view()),

    # /customer/Vehicle/?vehicle_id=&customer_id=1&authkey=
    url('Vehicle/', views.VehicleView.as_view()),

    #     # Billing APIS
    #     # /customer/CreateBill/?customer_id=1&authkey=?app_id=
    url('CreateBill/', views.CreateBill.as_view()),

    #     # Coupon APIS
    # /customer/Coupons/?customer_id=1&authkey=
    url('Coupons/', views.GetCoupons.as_view()),
    url('Banners/', views.Banners.as_view()),
    url('AppInfo/', views.AppInfoView.as_view()),
    url('Notification/', views.CustomerNotificationList.as_view()),
    url('Rating/', views.Rating.as_view()),
    url('UpdateCustomerCredit/', views.UpdateCustomerCredit.as_view()),
    url('SubscriptionTypeList/', views.SubscriptionTypeList.as_view()),
    url('SearchView/', views.SearchView.as_view()),
    url('CheckCoupon/', views.CheckCoupon.as_view()),
    url('RazerpayOrder/', views.RazerpayOrder.as_view()),
    url('SignatureVerification/', views.SignatureVerification.as_view()),
    url('AminitiesList/', views.AminitiesList.as_view()),

]
urlpatterns = format_suffix_patterns(urlpatterns)
