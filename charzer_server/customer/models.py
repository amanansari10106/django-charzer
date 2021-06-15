
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from passlib.hash import pbkdf2_sha256
from django.db.models import Sum


class SubscriptionType(models.Model):
    def __str__(self):
        return self.s_type+" Subscription"
    s_type_id = models.AutoField(primary_key=True)
    s_type = models.CharField(max_length=100)
    s_title = models.CharField(max_length=100)
    s_description = models.CharField(max_length=100)
    s_price = models.IntegerField(default=0)
    s_discount_price = models.IntegerField(default=0)
    s_percentage = models.IntegerField(default=0)


class Customers(models.Model):
    def __str__(self):
        return self.customer_name

    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100, default="User Name")
    email_regex = RegexValidator(
        regex=r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', message="Not a valid email")
    customer_email = models.CharField(max_length=100, validators=[
                                      email_regex], blank=True, null=True)

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,10}$', message="Phone number must be entered in the format +919999999999. Up to 10 digits allowed.")
    customer_phone = models.CharField('Phone', validators=[
        phone_regex], max_length=10, unique=True, default="")
    customer_image = models.ImageField(
        upload_to='Images/customer/customer_profile', default='Images/defaultProfile.png')
    customer_address = models.CharField(
        max_length=100, default="", blank=True, null=True)
    customer_credits = models.FloatField(max_length=200, default=0)
    customer_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    customer_referal = models.CharField(
        max_length=100, default='', unique=True)
    subscription = models.ForeignKey(
        SubscriptionType, on_delete=models.CASCADE, blank=True, null=True)
    subscription_start = models.DateTimeField(blank=True, null=True)
    subscription_end = models.DateTimeField(blank=True, null=True)
    customer_token = models.CharField(max_length=300, default='**')

    def verifyToken(self, token):
        return pbkdf2_sha256.verify(token, self.customer_token)


class PhoneOTP(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,10}$', message="Phone number must be entered in the format +919999999999. Up to 14 digits allowed.")
    phone = models.CharField(
        validators=[phone_regex], max_length=17, unique=True)
    otp = models.CharField(max_length=9, blank=True, null=True)
    count = models.IntegerField(default=0, help_text='Number of otp_sent')
    validated = models.BooleanField(
        default=False, help_text='If it is true, that means user have validate otp correctly in second API')
    otp_session_id = models.CharField(max_length=120, null=True, default="")

    def __str__(self):
        return str(self.phone)


class Vehicle(models.Model):
    def __str__(self):
        return self.vehicle_type+" "+self.vehicle_manufacture

    vehicle_id = models.AutoField(primary_key=True)
    vehicle_image = models.ImageField(
        upload_to='Images/customer/vehicle', default='Images/vehicle-placeholder.png')
    vehicle_customer = models.ForeignKey(
        Customers,  on_delete=models.CASCADE)
    vehicle_manufacture = models.CharField(max_length=100, default="")
    vehicle_model = models.CharField(max_length=100, default="")
    vehicle_type = models.CharField(max_length=100)
    is_favourite = models.BooleanField(default=True)


class Host(models.Model):
    def __str__(self):
        return self.host_name

    host_id = models.AutoField(primary_key=True)
    host_name = models.CharField(max_length=100, default='Host')
    hemail_regex = RegexValidator(
        regex=r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', message="Not a valid email")
    host_email = models.CharField(max_length=100, validators=[
        hemail_regex], blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,10}$', message="Phone number must be entered in the format +919999999999. Up to 10 digits allowed.")
    host_phone = models.CharField('Phone', validators=[
        phone_regex], max_length=10, unique=True, default="")
    host_image = models.ImageField(
        upload_to='Images/Host/host_profile', default='Images/defaultProfile.png')
    host_address = models.CharField(
        max_length=100, default="", blank=True, null=True)
    host_credit = models.IntegerField(default=0)
    host_active = models.BooleanField(default=True)
    host_referal = models.CharField(max_length=100, default='', unique=True)
    # changed
    host_sponsor = models.CharField(max_length=100, default='Unknown')

    host_token = models.CharField(max_length=100, default='**')

    def verifyToken(self, token):
        return pbkdf2_sha256.verify(token, self.host_token)


class SocketType(models.Model):
    def __str__(self):
        return self.socket_name
    socket_id = models.AutoField(primary_key=True)
    socket_name = models.CharField(max_length=100, default="")
    socket_power = models.IntegerField(default=0)
    socket_image = models.ImageField(
        upload_to='Images/Host/socket_photos', default='Images/defaultSocket.png')


class Charger(models.Model):
    def __str__(self):
        return self.charger_name
    charger_id = models.AutoField(primary_key=True)
    charger_name = models.CharField(max_length=100)
    charger_longitude = models.FloatField()
    charger_latitude = models.FloatField()
    # changed
    charger_online = models.BooleanField(default='False')
    charger_address = models.CharField(max_length=500, default="")

    charger_rating = models.FloatField(default=0.0)
    charger_open = models.TimeField(blank=True, null=True)
    charger_close = models.TimeField(blank=True, null=True)

    charger_brand_logo = models.ImageField(
        upload_to='Images/Host/charger_photos', default='Images/defaultCharger.png')
    charger_host = models.ForeignKey(Host,
                                     on_delete=models.CASCADE)

    power_available = models.CharField(max_length=100, default='')
    Other_details = models.CharField(max_length=100, default='')

    @ property
    def noOfBooking(self):
        app = self.appointment_set.filter(app_status='Upcoming')
        noOfBooking = app.count()
        return noOfBooking

    @ property
    def Booking(self):
        booking = self.appointment_set.all()
        return booking

    @ property
    def Sockets(self):
        socket = self.chargersocket_set.all()
        return socket

    @ property
    def Photos(self):
        photo = self.photo_set.all()
        return photo

    @ property
    def Nearby(self):
        nearby = self.nearby_set.all()
        return nearby

    @ property
    def Availablility(self):
        available = self.chargersocket_set.filter(Socket_availabile__gt=0)
        if available:
            return True
        else:
            return False

    @ property
    def TotalChargerEarning(self):      
        chargerTotal = Bill_Details.objects.filter(bill_app__app_charger=self).aggregate(
            total=Sum('bill_amount'))

        return chargerTotal['total']

class ChargerSocket(models.Model):
        

    charger_id = models.ForeignKey(Charger,
                                   on_delete=models.CASCADE, blank=True, null=True)
    socket_type = models.ForeignKey(SocketType,
                                    on_delete=models.CASCADE, blank=True, null=True)
    hour_price = models.FloatField(default=0.0)
    KWh_price = models.FloatField(default=0.0)
    charger_capacity = models.IntegerField()
    Socket_availabile = models.IntegerField(default=0)


class Nearby(models.Model):
    nearby_type = models.CharField(max_length=100)
    nearby_name = models.CharField(max_length=100)
    nearby_latitude = models.FloatField(default=0.0)
    nearby_longitude = models.FloatField(default=0.0)
    nearby_image = models.ImageField(
        upload_to='Images/Host/charger_photos', default='Images/defaultCharger.png')
    address = models.CharField(max_length=250)
    charger_id = models.ForeignKey(Charger,
                                   on_delete=models.CASCADE, blank=True, null=True)


class Aminities(models.Model):
    def __str__(self):
        return self.Aminitie
    Aminitie = models.CharField(max_length=100, default='')


class Coupon(models.Model):
    def __str__(self):
        return self.coupon_code
    coupon_id = models.AutoField(primary_key=True)
    coupon_code = models.CharField(max_length=50, default='')
    coupon_type_choice = [('Percentage', 'Percentage'), ('Amount',
                                                         'Amount')]
    coupon_type = models.CharField(
        max_length=50,  null=True, choices=coupon_type_choice)
    coupon_amt = models.FloatField(default=0.0)
    coupon_amt_limit = models.FloatField(default=0.0)
    customer_list = models.CharField(
        max_length=1000000, default=0, blank=True, null=True)
    usage_limit = models.IntegerField(default=0)
    customer_limit = models.IntegerField(default=0)
    open_to = [('All', 'All'), ('Nobody',
                                'Nobody'), ('selected_customer_type_only', 'Selected customer type only')]
    open_choice = models.CharField(
        max_length=50,  null=True, choices=open_to)


class CreditType(models.Model):
    def __str__(self):
        return self.credit_name
    credit_name = models.CharField(max_length=100, default="")
    credit_amt = models.FloatField(default=0.0)


class Credit(models.Model):
    def __str__(self):
        return str(self.credit_customer) + str(self.credit_type)
    credit_id = models.AutoField(primary_key=True)
    credit_customer = models.ForeignKey(
        Customers, on_delete=models.CASCADE)
    credit_type = models.ForeignKey(
        CreditType, on_delete=models.CASCADE)
    # status: True means credit was increased, false means credit was decreased
    credit_status = models.BooleanField(default=True)


class Photo(models.Model):
    charger_photo = models.ImageField(
        upload_to='Images/Host/charger_photos', default='Images/defaultCharger.png')
    Charger_id = models.ForeignKey(
        Charger, on_delete=models.CASCADE)


class FavouriteCharger(models.Model):
    def __str__(self):
        return str(self.favourite_customer)

    favourite_ID = models.AutoField(primary_key=True)
    favourite_charger = models.ForeignKey(
        Charger, on_delete=models.CASCADE)
    favourite_customer = models.ForeignKey(
        Customers,  on_delete=models.CASCADE)


class Appointment(models.Model):
    def __str__(self):
        return "APP"+str(self.app_customer)+"/"+str(self.app_id)
    app_id = models.AutoField(primary_key=True)
    app_customer = models.ForeignKey(
        Customers, on_delete=models.CASCADE)
    app_charger = models.ForeignKey(
        Charger,  on_delete=models.CASCADE)
    app_socket = models.ForeignKey(
        ChargerSocket,  on_delete=models.CASCADE)
    app_date_time = models.DateTimeField(blank=True, null=True)
    app_create_date = models.DateField(auto_now_add=True)
    app_create_time = models.TimeField(auto_now_add=True)
    app_amt = models.FloatField(default=0.0)
    app_duration = models.FloatField(max_length=100)
    status_choice = [('Completed', 'Completed'), ('Upcoming',
                                                  'Upcoming'), ('Cancelled', 'Cancelled'), ('Pending', 'Pending')]
    app_status = models.CharField(
        max_length=50,  null=True, choices=status_choice)
    app_socket = models.ForeignKey(
        ChargerSocket, on_delete=models.CASCADE, blank=True, null=True)


class Bill_Details(models.Model):
    def __str__(self):
        return "BILL"+str(self.bill_id)

    bill_id = models.AutoField(primary_key=True)
    bill_date = models.DateField(auto_now_add=True)
    bill_time = models.TimeField(auto_now_add=True)
    bill_amount = models.FloatField(max_length=100)
    razerpay_payment_id = models.CharField(max_length=100, default="")
    razerpay_order_id = models.CharField(max_length=100, default="")
    razerpay_signature = models.CharField(max_length=100, default="")
    bill_app = models.ForeignKey(
        Appointment, on_delete=models.CASCADE)
    coupon = models.ForeignKey(
        Coupon, on_delete=models.CASCADE, blank=True, null=True)
    bill_host = models.ForeignKey(
        Host, on_delete=models.CASCADE, blank=True, null=True)

    @property
    def totalCredit(self):
        host = self.bill_host
        totalCredit = host.host_credit
        return totalCredit


class SubAdmin(models.Model):
    subadmin = models.OneToOneField(
        User, on_delete=models.CASCADE, default=1)
    subadmin_email = models.CharField(max_length=100)
    subadmin_active = models.FloatField()

    def __str__(self):
        return self.user.username


class SubAdminAccess(models.Model):
    access_id = models.AutoField(primary_key=True)
    edit_user = models.BooleanField(default=False)
    edit_host = models.BooleanField(default=False)
    edit_billdetails = models.BooleanField(default=False)
    edit_pumpdetails = models.BooleanField(default=False)
    edit_appointments = models.BooleanField(default=False)
    access_subadmin = models.ForeignKey(
        SubAdmin,   on_delete=models.CASCADE)


class Ads(models.Model):
    def __str__(self):
        return "ad"+str(self.add_id)
    add_id = models.AutoField(primary_key=True)
    ad_description = models.CharField(max_length=500, blank=True, null=True)
    ad_option = [('Banner', 'Banner'), ('Promotional',
                                        'Promotional')]
    ad_frequency = models.IntegerField(default=0)
    ad_type = models.CharField(
        max_length=50, choices=ad_option, default='Promotional')
    ad_logo = models.ImageField(
        upload_to='Images/banner', blank=True, null=True)


class AppInfo(models.Model):
    PrivacyPolicy = models.TextField(
        max_length=5000, default="")
    TermsCondition = models.TextField(
        max_length=5000, default="")

    currency_choice = [('USD', 'USD'), ('INR', 'INR'),
                       ('EUR', 'EUR'), ('JPY', 'JPY'), ('GBP', 'GBP'), ('AUD', 'AUD'), ('CAD', 'CAD'), ('CHF', 'CHF')]
    AppCreditValue = models.FloatField(default=1.0)
    AppCurrency = models.CharField(
        max_length=10, default='USD', choices=currency_choice)
    Service_tax = models.FloatField(default=1.0)
    ContactUs = models.TextField(
        max_length=5000, default="")
    # ContactUs = models.TextField(
    #     max_length=5000, default="")

    @property
    def Help(self):
        help = Help.objects.all()
        return help


class Help(models.Model):
    def __str__(self):
        return self.Question
    Question = models.TextField(
        max_length=5000, default="")
    Answer = models.TextField(
        max_length=5000, default="")
    Date_time = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)


class CustomerNotification(models.Model):
    N_id = models.AutoField(primary_key=True)
    N_customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    N_Title = models.CharField(max_length=500, default="")
    N_Description = models.CharField(max_length=500, default="")
    N_date_time = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)

    N_status = models.BooleanField(default=True)


class ChargerRating(models.Model):
    rating_id = models.AutoField(primary_key=True)
    rating = models.IntegerField(default=0)
    rating_customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    rating_charger = models.ForeignKey(Charger, on_delete=models.CASCADE)
