from customer.models import *
from customer.serializers import *
from .models import *


class HostSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = "__all__"


class EditHost(serializers.ModelSerializer):

    class Meta:
        model = Host
        fields = ('host_id', 'host_name', 'host_email',
                  'host_phone', 'host_image', 'host_address')


class ChargerListSerializer(serializers.ModelSerializer):
    Nearby = NearbySerializer(many=True)
    Sockets = ChargerSocketSerialiser(many=True)
    Photos = PhotosSerializer(many=True)
    charger_host = ChargerHostSerialiser()
    noOfBooking = serializers.ReadOnlyField(default=0)
    TotalChargerEarning = serializers.ReadOnlyField(default=0)

    class Meta:
        model = Charger
        fields = ('charger_id', 'charger_name', 'charger_longitude', 'charger_latitude', 'charger_online',
                  'charger_rating', 'charger_address', 'charger_online',
                  'charger_open', 'charger_close', 'charger_brand_logo', 'charger_host', 'power_available',  'Other_details', 'Sockets', 'Photos', 'Nearby', 'noOfBooking', 'TotalChargerEarning')


class AddSocketSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargerSocket
        fields = "__all__"


class AddPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = "__all__"


class BillAppointmentSerialiser(serializers.ModelSerializer):
    app_customer = EditCustomerProfileSerializer()
    app_charger = ChargeringStationSerialiser()

    class Meta:
        model = Appointment
        fields = ('app_id', 'app_charger', 'app_date_time', 'app_amt',
                  'app_duration', 'app_status', 'app_customer')


class BillingViewSerialiser(serializers.ModelSerializer):
    coupon = CouponSerializer()
    bill_app = BillAppointmentSerialiser()
    totalCredit = serializers.ReadOnlyField(default=0)

    class Meta:
        model = Bill_Details
        fields = ('bill_id', 'bill_date', 'bill_time', 'bill_amount',
                  'razerpay_payment_id', 'coupon', 'razerpay_order_id', 'razerpay_signature', 'bill_app', 'totalCredit')


class CreateCharger(serializers.ModelSerializer):

    class Meta:
        model = Charger
        fields = ("charger_id",
                  "charger_name",
                  "charger_longitude",
                  "charger_latitude",
                  "charger_open",
                  "charger_address",
                  "charger_close",
                  "charger_brand_logo",
                  "charger_host",
                  "power_available",
                  "Other_details",
                  )


class EditChargerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Charger
        fields = ("charger_id",
                  "charger_name",
                  "charger_longitude",
                  "charger_latitude",
                  "charger_open",
                  "charger_close",
                  "charger_brand_logo",
                   "charger_address",
                  "power_available",
                  "Other_details",
                  )


class HostNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostNotification
        fields = "__all__"
