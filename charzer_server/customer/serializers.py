from rest_framework import serializers
from .models import *


# All


class CustomerSerialiser(serializers.ModelSerializer):

    class Meta:
        model = Customers
        fields = "__all__"


class BookmarkEditSerialiser(serializers.ModelSerializer):

    class Meta:
        model = FavouriteCharger
        fields = "__all__"


class AppointmentCreateSerialiser(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = "__all__"


class VehicleSerialiser(serializers.ModelSerializer):

    class Meta:
        model = Vehicle
        fields = "__all__"


class BillingCreateSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Bill_Details
        fields = "__all__"


class AminitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aminities
        fields = "__all__"


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionType
        fields = "__all__"


class SocketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocketType
        fields = "__all__"


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargerRating
        fields = "__all__"


class CreditTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditType
        fields = "__all__"


class EditCustomerProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customers
        fields = ('customer_id', 'customer_name', 'customer_email',
                  'customer_phone', 'customer_image', 'customer_address')


class GetCustomerSerializer(serializers.ModelSerializer):
    subscription = SubscriptionSerializer(read_only=True)

    class Meta:
        model = Customers
        fields = ('customer_id', 'customer_name', 'customer_email',
                  'customer_phone', 'customer_image', 'customer_address', 'customer_credits', 'customer_active', 'customer_referal', 'subscription', 'subscription_start', 'subscription_end')


class ChargerHostSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ['host_id', 'host_name',
                  'host_address', 'host_email', 'host_image', 'host_phone', 'host_sponsor']


class ChargerSocketSerialiser(serializers.ModelSerializer):
    socket_type = SocketTypeSerializer()

    class Meta:
        model = ChargerSocket
        fields = "__all__"


class PhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = "__all__"


class NearbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Nearby
        fields = '__all__'


class ChargeringStationSerialiser(serializers.ModelSerializer):
    Nearby = NearbySerializer(many=True)
    Sockets = ChargerSocketSerialiser(many=True)
    charger_host = ChargerHostSerialiser()
    Photos = PhotosSerializer(many=True)
    Availablility = serializers.ReadOnlyField(default=True)
    # IsFavourate = serializers.ReadOnlyField(default=False)

    class Meta:
        model = Charger
        fields = ('charger_id', 'charger_name', 'charger_longitude', 'charger_latitude', 'charger_online',
                  'Availablility',
                  'charger_rating', 'charger_address',
                  'charger_open', 'charger_close', 'charger_brand_logo', 'charger_host', 'power_available', 'Other_details', 'Sockets', 'Photos', 'Nearby')


class BookmarkSerialiser(serializers.ModelSerializer):
    favourite_charger = ChargeringStationSerialiser(
    )

    class Meta:
        model = FavouriteCharger
        fields = ('favourite_ID', 'favourite_charger',
                  'favourite_customer')


class AppointmentSerialiser(serializers.ModelSerializer):
    app_customer = CustomerSerialiser()
    app_charger = ChargeringStationSerialiser()
    app_socket = ChargerSocketSerialiser()

    class Meta:
        model = Appointment
        fields = ('app_id', 'app_customer', 'app_charger',
                  'app_date_time', 'app_amt', 'app_create_date', 'app_create_time',  'app_duration', 'app_status', 'app_socket')


class VehicleEditSerialiser(serializers.ModelSerializer):

    class Meta:
        model = Vehicle
        fields = '__all__'


class ReferalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customers
        fields = ['customer_referal', 'customer_credits']


class EditAppointment(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['app_status']


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ads
        fields = "__all__"


class HelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Help
        fields = "__all__"


class AppInfoSerializer(serializers.ModelSerializer):
    Help = HelpSerializer(many=True)

    class Meta:
        model = AppInfo
        fields = ('PrivacyPolicy', 'TermsCondition',
                  'AppCurrency', 'Service_tax', 'AppCreditValue', 'ContactUs', 'Help')


class CustomerNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerNotification
        fields = "__all__"
