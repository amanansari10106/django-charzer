from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *


@admin.register(Customers)
class usrdet(ImportExportModelAdmin):
    pass


admin.site.register(Aminities)
admin.site.register(Nearby)
admin.site.register(Vehicle)
admin.site.register(Host)
admin.site.register(Charger)
admin.site.register(FavouriteCharger)
admin.site.register(Appointment)
admin.site.register(Bill_Details)
admin.site.register(SubAdmin)
admin.site.register(SubAdminAccess)
admin.site.register(Ads)
admin.site.register(SubscriptionType)
admin.site.register(ChargerSocket)
admin.site.register(SocketType)
admin.site.register(Coupon)
admin.site.register(Credit)
admin.site.register(CreditType)
admin.site.register(Photo)
admin.site.register(PhoneOTP)
admin.site.register(AppInfo)
admin.site.register(CustomerNotification)
admin.site.register(ChargerRating)
admin.site.register(Help)
