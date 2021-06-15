from passlib.hash import pbkdf2_sha256
import json
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q
from .models import *
from .serializers import *
from rest_framework import viewsets, status
from django.shortcuts import render, get_object_or_404
import urllib.parse
import requests
import string
import random
# import mysql.connector
from hashlib import blake2b
from rest_framework import generics
from django.db.models import Sum
from rest_framework.views import APIView
import math
import urllib
import urllib.request as urllib2
from django.http import Http404
from django.core.signing import Signer
from collections import Counter
from django.views.decorators.csrf import csrf_exempt
import uuid
import razorpay
client = razorpay.Client(
    auth=('rzp_test_IWhTimX0VPArVr', 'QRhlLUiKseMeMcxExXeqExOp'))

# Order


class RazerpayOrder(APIView):
    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        charger = Charger.objects.all()
        return charger

    def get(self, request, *args, **kwargs):
        customer_id = request.query_params['customer_id']
        amount = request.query_params['amount']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            order_amount = int(amount)
            appInfo = AppInfo.objects.get(pk=1)

            order_currency = appInfo.AppCurrency

            response = client.order.create(dict(
                amount=order_amount, currency=order_currency))

            order_id = response['id']
            order_status = response['status']
            if order_status == 'created':
                return Response({'status': True, 'order_id': order_id})
            return Response({'message': "failed"})
        else:
            return Response({"status": "invalid authkey"})


class SignatureVerification(APIView):
    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        charger = Charger.objects.all()
        return charger

    def get(self, request, *args, **kwargs):
        customer_id = request.query_params['customer_id']
        razerpay_payment_id = request.query_params['razerpay_payment_id']
        razerpay_order_id = request.query_params['razerpay_order_id']
        razerpay_signature = request.query_params['razerpay_signature']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            try:
                status = client.utility.verify_payment_signature(dict(
                    razerpay_payment_id=razerpay_payment_id, razerpay_order_id=razerpay_order_id, razerpay_signature=razerpay_signature))
                return Response({'status': True, 'message': 'payment successful'})
            except:
                return Response({'status': False, 'message': 'payment failed'})
        else:
            return Response({"status": "invalid authkey"})

# Charger API


class ChargerDetail(APIView):
    serializer_class = ChargeringStationSerialiser

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        charger = Charger.objects.all()
        return charger

    def get(self, request, *args, **kwargs):
        charger_id = request.query_params['charger_id']
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        latitude = request.query_params.get('latitude', '')
        longitude = request.query_params.get('longitude', '')
        try:
            customer = Customers.objects.get(customer_id=customer_id)

        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):

            try:
                charger = Charger.objects.get(charger_id=charger_id)
                fav = FavouriteCharger.objects.get(
                    favourite_customer=customer, favourite_charger=charger)
                newdict = {'IsFav': True,'favourite_ID': fav.favourite_ID}
            except Charger.DoesNotExist:
                return Response({"status": "charger not found"})
            except FavouriteCharger.DoesNotExist:
                newdict = {'IsFav': False }
            serializer = ChargeringStationSerialiser(charger)
            
            newdict.update(serializer.data)
            return Response(newdict)
        else:
            return Response({
                "message": "invalid authkey"
            })


# Vehicle API

class VehicleList(APIView):
    serializer_class = VehicleSerialiser

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        vehicles = Vehicle.objects.all()
        return vehicles

    def get(self, request, *args, **kwargs):
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            try:
                customer = Customers.objects.get(customer_id=customer_id)
                vehicles = customer.vehicle_set.all()
            except Customers.DoesNotExist:
                return Response({"status": "customer not found"})
            if vehicles:
                serializer = VehicleSerialiser(vehicles, many=True)
                return Response(serializer.data)
            return Response({"status": "no vehicle available"})
        else:
            return Response({"status": "invalid authkey"})

# #
# # Details of an Vehicle
# #


class VehicleView(APIView):
    serializer_class = VehicleEditSerialiser

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        vehicle = Vehicle.objects.all()
        return vehicle

    def get(self, request, *args, **kwargs):
        vehicle_id = request.query_params['vehicle_id']
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):

            try:
                vehicle = Vehicle.objects.get(
                    vehicle_id=vehicle_id)
            except Vehicle.DoesNotExist:
                return Response({"status": "not found"})
            serializer = VehicleSerialiser(vehicle)
            return Response(serializer.data)
        else:
            return Response({"status": "invalid authkey"})

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        vehicle_id = request.query_params['vehicle_id']
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            try:
                vehicle = Vehicle.objects.get(vehicle_id=vehicle_id)
            except Vehicle.DoesNotExist:
                return Response({"status": "not found"})
            serializer = VehicleEditSerialiser(vehicle, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "invalid authkey"})

    def delete(self, request, *args, **kwargs):
        vehicle_id = request.query_params['vehicle_id']
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            try:
                vehicle = Vehicle.objects.get(vehicle_id=vehicle_id)
            except Vehicle.DoesNotExist:
                return Response({"status": "not found"})
            vehicle.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"status": "invalid authkey"})

    @csrf_exempt
    def post(self, request, format=None):
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            vehicle = VehicleSerialiser(data=request.data)
            if vehicle.is_valid():
                vehicle.save()
                return Response(vehicle.data, status=status.HTTP_201_CREATED)
            return Response(vehicle.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "invalid authkey"})


# #
# List of Appointments of a customer
# #

class AppointmentList(APIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerialiser

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, request, *args, **kwargs):
        customer_id = request.query_params['customer_id']

        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            try:
                customer = Customers.objects.get(customer_id=customer_id)
                appointment = customer.appointment_set.all()
            except Customers.DoesNotExist:
                return Response({"status": "customer not found"})
            if appointment:
                serializer = AppointmentSerialiser(appointment, many=True)
                return Response(serializer.data)
            return Response({"status": "no appointment available"})
        else:
            return Response({"status": "invalid authkey"})


# # #
# # # Details of an Apponiment ad edit
# # #


class GetAppointment(APIView):
    serializer_class = AppointmentSerialiser

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        chargers = Appointment.objects.all()
        return chargers

    def get(self, request, *args, **kwargs):
        app_id = request.query_params['app_id']
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            try:
                appointment = Appointment.objects.get(
                    app_id=app_id)
            except Appointment.DoesNotExist:
                return Response({"status": "not found"})
            serializer = AppointmentSerialiser(appointment)
            return Response(serializer.data)
        else:
            return Response({"status": "invalid authkey"})


class ChangeStatusAppointment(APIView):
    serializer_class = EditAppointment

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        chargers = Appointment.objects.all()
        return chargers

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        app_id = request.query_params['app_id']
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            try:
                appointment = Appointment.objects.get(
                    app_id=app_id)
            except Appointment.DoesNotExist:
                return Response({"status": "not found"})
            serializer = EditAppointment(
                appointment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "invalid authkey"})

    def delete(self, request, *args, **kwargs):
        app_id = request.query_params['app_id']
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            try:
                appointment = Appointment.objects.get(
                    app_id=app_id)
            except Appointment.DoesNotExist:
                return Response({"status": "not found"})
            appointment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"status": "invalid authkey"})


class CreateAppointment(APIView):
    serializer_class = AppointmentCreateSerialiser

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        chargers = Appointment.objects.all()
        return chargers

    # def get(self, request, *args, **kwargs):
    #     app_id = request.query_params['app_id']
    #     customer_id = request.query_params['customer_id']
    #     token = request.query_params['authkey']
    #     try:
    #         customer = Customers.objects.get(customer_id=customer_id)
    #     except:
    #         return Response({'message': 'invalid customer_id'})

    #     if customer.verifyToken(token):
    #         try:
    #             appointment = Appointment.objects.get(
    #                 app_id=app_id)
    #         except Appointment.DoesNotExist:
    #             return Response({"status": "not found"})
    #         serializer = AppointmentCreateSerialiser(appointment)
    #         return Response(serializer.data)
    @csrf_exempt
    def post(self, request, format=None):
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']

        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            try:
                pending = customer.appointment_set.get(app_status='Pending')
                return Response({'status': False, 'message': 'pending payment'})
            except:

                try:
                    chargerSocket = ChargerSocket.objects.get(
                        pk=request.data["app_socket"])
                except:
                    return Response({'status': False, 'message': chargerSocket})

                chargerSocket.Socket_availabile -= 1
                chargerSocket.save()
                appointment = AppointmentCreateSerialiser(data=request.data)
                if appointment.is_valid():
                    appointment.save()
                    return Response(appointment.data, status=status.HTTP_201_CREATED)
                return Response(appointment.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "invalid authkey"})


# class Appointments(APIView):
#     serializer_class = AppointmentSerialiser

#     @classmethod
#     def get_extra_actions(cls):
#         return []

#     def get_queryset(self):
#         chargers = Appointment.objects.all()
#         return chargers

#     def get(self, request, *args, **kwargs):
#         app_id = request.query_params['app_id']
#         customer_id = request.query_params['customer_id']
#         token = request.query_params['authkey']
#         try:
#             customer = Customers.objects.get(customer_id=customer_id)
#         except:
#             return Response({'message': 'invalid customer_id'})

#         if customer.verifyToken(token):
#             try:
#                 appointment = Appointment.objects.get(
#                     app_id=app_id)
#             except Appointment.DoesNotExist:
#                 return Response({"status": "not found"})
#             serializer = AppointmentSerialiser(appointment)
#             return Response(serializer.data)
#         else:
#             return Response({"status": "invalid authkey"})

# #
# # Bookmark APIViews
# #


class BookmarkList(generics.ListAPIView):
    # queryset = FavouriteCharger.objects.all()
    serializer_class = BookmarkSerialiser

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        chargers = FavouriteCharger.objects.all()
        return chargers

    def get(self, request, *args, **kwargs):
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            try:
                customer = Customers.objects.get(customer_id=customer_id)
                chargers = customer.favouritecharger_set.all()
            except:
                return Response({"status": "customer not found"})
            if chargers:
                serializer = BookmarkSerialiser(chargers, many=True)
                return Response(serializer.data)
            return Response({"status": "no bookmark available"})

        else:
            return Response({"status": "invalid authkey"})

#
# give a charger that is bookmarked
#


class BookmarkCharger(APIView):
    serializer_class = BookmarkSerialiser

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        chargers = FavouriteCharger.objects.all()
        return chargers

    def get(self, request, *args, **kwargs):
        bookmark_id = request.query_params['favourite_ID']
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            try:
                charger = FavouriteCharger.objects.get(
                    favourite_ID=bookmark_id)
            except FavouriteCharger.DoesNotExist:
                return Response({"status": "not found"})
            serializer = BookmarkSerialiser(charger)
            return Response(serializer.data)
        else:
            return Response({"status": "invalid authkey"})


class EditBookmarkCharger(APIView):
    serializer_class = BookmarkEditSerialiser

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        chargers = FavouriteCharger.objects.all()
        return chargers

    def get(self, request, *args, **kwargs):
        bookmark_id = request.query_params['favourite_ID']
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            try:
                charger = FavouriteCharger.objects.get(
                    favourite_ID=bookmark_id)
            except FavouriteCharger.DoesNotExist:
                return Response({"status": "not found"})
            serializer = BookmarkEditSerialiser(charger)
            return Response(serializer.data)
        else:
            return Response({"status": "invalid authkey"})

    def delete(self, request, *args, **kwargs):
        bookmark_id = request.query_params['favourite_ID']
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})
        if customer.verifyToken(token):
            try:
                charger = FavouriteCharger.objects.get(
                    favourite_ID=bookmark_id)
            except FavouriteCharger.DoesNotExist:
                return Response({"status": "not found"})
            charger.delete()
            return Response({'status':True, 'message':'deleted'})
        else:
            return Response({"status": "invalid authkey"})

    @csrf_exempt
    def post(self, request, format=None):

        customer_id = request.query_params['customer_id']

        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)

        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            try:
                charger = FavouriteCharger.objects.get(favourite_charger=request.data['favourite_charger'],favourite_customer=customer)
                charger.delete()
                return Response({"status": "deleted"})
            except FavouriteCharger.DoesNotExist:
                bookmark = BookmarkEditSerialiser(data=request.data)
                if bookmark.is_valid():
                    bookmark.save()
                    return Response(bookmark.data, status=status.HTTP_201_CREATED)
                return Response(bookmark.errors, status=status.HTTP_400_BAD_REQUEST)
            
            
        else:
            return Response({"status": "invalid authkey"})
# coupon Api


class GetCoupons(APIView):

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        coupons = Coupon.objects.all()
        return coupons

    def get(self, request, *args, **kwargs):

        coupons = Coupon.objects.all()
        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data)


# # billing Apis


class CreateBill(APIView):
    serializer_class = BillingCreateSerialiser

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        bills = Bill_Details.objects.all()
        return bills

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        appointment = request.query_params['app_id']
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
            app = Appointment.objects.get(app_id=appointment)
        except:
            return Response({'message': 'invalid data'})

        if customer.verifyToken(token):
            if app.app_status == 'Completed':
                return Response({'status': False, 'message': 'Already Payed'})
            serializer = BillingCreateSerialiser(data=request.data)
            if serializer.is_valid():
                serializer.save()
                chargerSocket = ChargerSocket.objects.get(id=app.app_socket.id)
                chargerSocket.Socket_availabile += 1
                chargerSocket.save()
                host = app.app_charger.charger_host
                host.host_credit += int(
                    request.data['bill_amount'])
                host.save()
                app.app_status = 'Completed'
                app.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "invalid authkey", 'app': app.app_charger.charger_host.host_credit, 'amt': int(request.data['bill_amount'])})

# # class CustomerViewSet(APIView):
# #     # queryset = Customers.objects.all()
# #     # serializer_class = CustomerSerialiser

# #     @classmethod
# #     def get_extra_actions(cls):
# #         return []

# #     def get_queryset(self):
# #         customer = Customers.objects.all()
# #         return customer

#     # def get(self, request, *args, **kwargs):
#     #     customer_id = request.query_params['customer_id']
#     #     token = request.query_params['authkey']
#     #     try:
#     #         customer = Customers.objects.get(customer_id=customer_id)
#     #     except:
#     #         return Response({'message': 'invalid customer_id'})

#     #     if customer.verifyToken(token):

#     #         queryset = self.get_queryset()
#     #         if queryset:
#     #             serializer = CustomerSerialiser(queryset, many=True)
#     #             return Response(serializer.data)
#     #         return Response({"status": "no customer found"})
#     #     else:
#     #         return Response({"status":"invalid authkey"})

# # #
# # # customer profile
# # #


class Profile(APIView):
    serializer_class = EditCustomerProfileSerializer

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        customer = Customers.objects.all()
        return customer

    def get(self, request, *args, **kwargs):

        id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=id)
        except Customers.DoesNotExist:
            return Response({"status": "not found"})
        customer_id = request.query_params['customer_id']
        if customer.verifyToken(token):
            serializer = GetCustomerSerializer(customer)
            return Response(serializer.data)
        else:
            return Response({"status": "invalid authkey"})

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=id)
        except Customers.DoesNotExist:
            return Response({"status": "not found"})
        if customer.verifyToken(token):
            serializer = EditCustomerProfileSerializer(
                customer, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "invalid authkey"})

# # #
# # # To get, check referal id and update the credits
# # #


class Referal(APIView):
    # queryset = Customers.objects.all()
    # serializer_class = CustomerSerialiser

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        customers = Customers.objects.all()
        return customers

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        referalID = request.query_params['referalID']
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            credit = CreditType.objects.get(credit_name='Refer')
            amt = credit.credit_amt
            customer = Customers.objects.get(customer_id=customer_id)
            if customer.customer_referal == referalID:
                return Response({"status": "Invalid referal ID "})

            try:
                customer_refered = Customers.objects.exclude(
                    customer_id=customer_id).get(customer_referal=referalID)

            except Customers.DoesNotExist:
                return Response({"status": "Invalid referal ID "})
            customer.customer_credits += amt
            customer_refered.customer_credits += amt
            customer.save()
            customer_refered.save()
            credit_detail = Credit.objects.create(
                credit_customer=customer, credit_type=credit, credit_status=True)
            refered_credit_detail = Credit.objects.create(
                credit_customer=customer_refered, credit_type=credit, credit_status=True)
            credit_detail.save()
            refered_credit_detail.save()

            return Response({"status": "valid referal ID "})
        else:
            return Response({"status": "invalid authkey"})


# otp verification


class ValidatePhoneSendOTP(APIView):
    # serializer_class = VerificationSerialiser
    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        phone = PhoneOTP.objects.all()
        return phone

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        authkey = "266785AMp0UB2Tv55f85d9fcP1"
        mobiles = request.data.get('phone')
        message = urllib.parse.quote("CHARZER OTP is: ")
        Secret_hash = b'asd2c1fsa25s'
        h = blake2b(digest_size=16, person=Secret_hash)
        sender = "CHARZER"
        if mobiles:
            phone = str(mobiles)
            mobile = str(mobiles).encode(encoding='UTF-8')
            h.update(mobile)

            try:
                customer = Customers.objects.get(customer_phone=phone)
            except Customers.DoesNotExist:
                pass
            key = send_otp(phone)
            if key:
                try:
                    old = PhoneOTP.objects.get(phone=phone)
                except:
                    obj = PhoneOTP.objects.create(
                        phone=phone
                    )
                    url = f"""http://api.msg91.com/api/v2/sendsms?authkey={authkey}&mobiles={mobiles}&message={message}{key}&sender={sender}&route=4&country=91"""

                    response = requests.get(url)
                    output = json.loads(response.text)

                    if output["type"] == 'success':

                        obj.otp_session_id = generate(phone)
                        obj.otp = key
                        obj.save()

                        return Response({

                            'status': True,
                            'detail': 'OTP sent successfully'
                        })
                    else:
                        return Response({
                            'status': False,
                            'detail': 'OTP sending Failed'
                        })

                if old:
                    count = old.count
                    if count > 10:
                        return Response({
                            'status': False,
                            'detail': 'Sending otp error. Limit Exceeded. Please Contact Customer support'
                        })

                    old.count = count + 1
                    old.save()

                    url = f"""http://api.msg91.com/api/v2/sendsms?authkey={authkey}&mobiles={mobiles}&message={message}{key}&sender={sender}&route=4&country=91"""
                    response = requests.get(url)
                    output = json.loads(response.text)

                    if output["type"] == 'success':

                        old.otp = key
                        old.save()

                        return Response({
                            'status': True,
                            'detail': 'OTP sent successfully'
                        })
                    else:
                        return Response({
                            'status': False,
                            'detail': 'OTP sending Failed'
                        })

                else:
                    return Response({
                        'status': False,
                        'detail': 'Sending otp error'
                    })

        else:
            return Response({
                'status': False,
                'detail': 'Phone number is not given in post request'
            })


def send_otp(phone):
    if phone:
        key = random.randint(999, 9999)
        print(key)
        return key
    else:
        return False


def generate(phone):
    if phone:
        length = random.randint(0, 75)
        key = pbkdf2_sha256.encrypt(phone)
        key = str(key)
        token = key[length:(length+15)]+str(uuid.uuid4().hex[:5])
        return token


# for registeration


class ValidateOTP(APIView):
    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        phone = PhoneOTP.objects.all()
        return phone

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        otp_sent = request.data.get('otp', False)
        phone = str(phone)
        if phone and otp_sent:
            try:
                old = PhoneOTP.objects.get(phone=phone)

            except:
                return Response({
                    'status': False,
                    'detail': 'First Proceed via sending otp request'
                })

            if old.otp == str(otp_sent):

                try:
                    customer = Customers.objects.get(customer_phone=phone)
                    token = old.otp_session_id
                    customer.customer_token = pbkdf2_sha256.encrypt(token)
                    customer.save()
                    old.delete()
                    # customer = Customers.objects.get(customer_phone=phone)
                    return Response({
                        'authKey': token,
                        'customer id': customer.customer_id,
                        'status': True,
                        'detail': 'Customer logged in',

                    })
                except:
                    token = pbkdf2_sha256.encrypt(old.otp_session_id)
                    referralID = get_referral_id(old.phone)

                    customer_data = {
                        "customer_name": "User Name",
                        "customer_phone": old.phone,
                        "customer_referal": referralID,
                        "customer_token": token

                    }
                    serializer = CustomerSerialiser(data=customer_data)
                    if serializer.is_valid():
                        otp_session_id = old.otp_session_id
                        old.save()
                        serializer.save()
                        old.delete()
                        customer = Customers.objects.get(customer_phone=phone)
                        return Response({
                            'authkey': otp_session_id,
                            'customer id': customer.customer_id,
                            'status': True,
                            'detail': 'OTP MATCHED.User Registered '
                        })
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({
                    'status': False,
                    'detail': 'OTP INCORRECT'
                })

        else:
            return Response({
                'status': False,
                'detail': 'Please provide both phone and otp for Validation'
            })


def get_referral_id(phone):
    if phone:
        phone = int(phone)
        length = random.randint(1, 10)
        phone = phone*length
        key = hex(phone).lstrip("0x").rstrip("L")
        return key


# # Filter Charger


class Filter(APIView):

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        charger = Charger.objects.all()
        return charger

    def get(self, request, *args, **kwargs):
        power = request.query_params.get('power', '')
        socket = request.query_params.get('socket', '')
        amenities = request.query_params.get('amenities', '')
        parking = request.query_params.get('parking', '')
        networks = request.query_params.get('networks', '')
        distance = request.query_params.get('distance', '')
        latitude = request.query_params.get('latitude', '')
        longitude = request.query_params.get('longitude', '')
        online_status = request.query_params.get('online_status', False)
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']

        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            if distance != 0 and latitude and longitude:
                distance = int(distance)
                latitude = float(latitude)
                longitude = float(longitude)
                b = 2
                c = 3
                d = 5
                if distance <= b:
                    distance = 0.006
                elif b < distance <= c:
                    distance = 0.02
                elif c < distance <= d:
                    distance = 0.04
                elif d < distance:
                    distance = 0.2
                min_lat = latitude - distance
                max_lat = latitude + distance
                min_lng = longitude - distance
                max_lng = longitude + distance
                match = Charger.objects.filter(Q(power_available__icontains=power) & Q(charger_latitude__gt=min_lat, charger_latitude__lt=max_lat,
                                                                                       charger_longitude__gt=min_lng, charger_longitude__lt=max_lng) & Q(Other_details__icontains=amenities) & Q(Other_details__icontains=parking) & Q(charger_host__host_sponsor__icontains=networks))

                if online_status:
                    match = Charger.objects.filter(Q(power_available__icontains=power) & Q(charger_latitude__gt=min_lat, charger_latitude__lt=max_lat,
                                                                                           charger_longitude__gt=min_lng, charger_longitude__lt=max_lng) & Q(Other_details__icontains=amenities) & Q(Other_details__icontains=parking) & Q(charger_host__host_sponsor__icontains=networks) & Q(charger_online=online_status))
            
            serializer = ChargeringStationSerialiser( match, many=True )
            newdict = []
            #Done by kapil
            for i in range(len(serializer.data)):
                try:
                    charger = Charger.objects.get(charger_id= serializer.data[i]['charger_id'])
                    fav = FavouriteCharger.objects.get( favourite_customer=customer, favourite_charger=charger )
                    n_dict = {'IsFav': True,'favourite_ID': fav.favourite_ID}
                    n_dict.update(serializer.data[i])
                    newdict.append(n_dict)
                except Charger.DoesNotExist:
                    pass
                except FavouriteCharger.DoesNotExist:
                    n_dict = {'IsFav': False }
                    n_dict.update(serializer.data[i])
                    newdict.append(n_dict)
                          
            return Response(newdict)
        else:
            return Response({"status": "invalid authkey"})


class LogOut(generics.ListAPIView):

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        chargers = Customers.objects.all()
        return chargers

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            customer.customer_token = "**"
            customer.save()
            return Response({
                'status': True,
                'detail': 'Logged out successfully'
            })
        else:
            return Response({"status": "invalid authkey"})


class Subscribe(APIView):
    @classmethod
    def get_extra_actions(cls):
        return []

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        customer_id = request.query_params['customer_id']
        subscription_type = request.query_params['type']
        subscription_start = request.query_params['start']
        subscription_end = request.query_params['end']

        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})
        if customer.verifyToken(token):
            try:
                subs_type = SubscriptionType.objects.get(
                    s_type=subscription_type)

            except:
                return Response({'message': 'invalid subscription Type'})
            customer.subscription = subs_type
            customer.subscription_start = subscription_start
            customer.subscription_end = subscription_end
            customer.save()
            return Response({'status': True,
                             'detail': 'Subscrition Active'})


class Banners(generics.ListAPIView):
    serializer_class = BannerSerializer

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        ads = Ads.objects.all()
        return ads

    def get(self, request, *args, **kwargs):
        banners = Ads.objects.all()
        serializer = BannerSerializer(banners, many=True)
        return Response(serializer.data)


class CustomerNotificationList(APIView):
    serializer_class = CustomerNotificationSerializer

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        notification = CustomerNotification.objects.all()
        return notification

    def get(self, request, *args, **kwargs):
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            try:
                notification = CustomerNotification.objects.filter(
                    N_customer=customer)
            except:
                return Response({"status": "customer not found"})
            if notification:
                serializer = CustomerNotificationSerializer(
                    notification, many=True)
                return Response(serializer.data)
            return Response({"status": "no notification available"})
        else:
            return Response({"status": "invalid authkey"})

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        serializer = CustomerNotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)


class AppInfoView(generics.ListAPIView):

    serializer_class = AppInfoSerializer

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        appInfo = AppInfo.objects.all()
        return appInfo

    def get(self, request, *args, **kwargs):
        Info = AppInfo.objects.all()
        serializer = AppInfoSerializer(Info, many=True)
        return Response(serializer.data)


class Rating(APIView):
    serializer_class = RatingSerializer

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        rating = ChargerRating.objects.all()
        return rating

    def get(self, request, *args, **kwargs):
        rating = ChargerRating.objects.all()
        serializer = RatingSerializer(rating, many=True)
        return Response(serializer.data)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        customer_id = request.query_params['customer_id']
        token = request.query_params['authkey']
        charger_id = request.query_params['charger_id']
        try:
            customer = Customers.objects.get(customer_id=customer_id)
            charger = Charger.objects.get(charger_id=charger_id)
        except:
            return Response({'message': 'invalid customer_id'})

        if customer.verifyToken(token):
            serializer = RatingSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                total_rating = ChargerRating.objects.filter(rating_charger=charger_id).aggregate(
                    total=Sum('rating'))
                rating_count = charger.chargerrating_set.all().count()
                charger.charger_rating = format(
                    total_rating['total']/rating_count, '.1f')
                charger.save()
                return Response({"status": True, "new rating": format(total_rating['total']/rating_count, '.1f')
                                 })
        else:
            return Response({"status": "invalid authkey"})


class UpdateCustomerCredit(APIView):
    # serializer_class = CustomerSerialiser

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        customer = Customers.objects.all()
        return customer

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        id = request.query_params['customer_id']
        token = request.query_params['authkey']
        credit = request.query_params['credit']
        credit = float(credit)

        try:
            customer = Customers.objects.get(customer_id=id)
        except Customers.DoesNotExist:
            return Response({"status": "not found"})
        if customer.verifyToken(token):
            new_credit = customer.customer_credits + credit
            if new_credit < 0:
                return Response({"status": False, "message": 'the credit can not be less than zero'})
            customer.customer_credits = new_credit
            customer.save()

            return Response({"status": True, "customer_credit": customer.customer_credits})
        else:
            return Response({"status": "invalid authkey"})


class AminitiesList(generics.ListAPIView):

    serializer_class = AminitiesSerializer

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        amn = Aminities.objects.all()
        return amn

    def get(self, request, *args, **kwargs):
        amn = Aminities.objects.all()
        serializer = AminitiesSerializer(amn, many=True)
        return Response(serializer.data)


class SubscriptionTypeList(generics.ListAPIView):

    serializer_class = SubscriptionSerializer

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        Subs = SubscriptionType.objects.all()
        return Subs

    def get(self, request, *args, **kwargs):
        subs = SubscriptionType.objects.all()
        serializer = SubscriptionSerializer(subs, many=True)
        return Response(serializer.data)


class SearchView(generics.ListAPIView):
    search_fields = ['charger_name', 'Other_details',
                     'power_available', 'charger_host__host_name', 'charger_host__host_address']
    filter_backends = (SearchFilter,)
    queryset = Charger.objects.all()
    serializer_class = ChargeringStationSerialiser


class CheckCoupon(APIView):

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        coupon = Coupon.objects.all()
        return coupon

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        coupon_code = request.query_params['coupon_code']
        customer_id = request.query_params['customer_id']
        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code)

        except:
            return Response({"status": False, "message": 'Invalid Coupon code'})
        res = Counter(coupon.customer_list.split("_"))
        if len(res) is coupon.customer_limit+1:
            return Response({"status": False, "message": 'Sorry,the coupon can not be used by anymore users'})
        usage_limit = coupon.usage_limit
        if str(customer_id) in res:
            if res[str(customer_id)] < usage_limit:
                coupon.customer_list += "_"+str(customer_id)
                coupon.save()
                if coupon.coupon_type == 'Percentage':
                    return Response({"status": True, "message": 'Valid Coupon', 'type': 'Percentage', 'percentage_off': coupon.coupon_amt, 'max_amount': coupon.coupon_amt_limit})
                elif coupon.coupon_type == 'Amount':
                    return Response({"status": True, "message": 'Valid Coupon', 'type': 'Amount', 'coupon_amount': coupon.coupon_amt, 'min_amount_limit': coupon.coupon_amt_limit})

            else:
                return Response({"status": False, "message": 'You have exceeded usage limit'})
        else:
            coupon.customer_list += "_"+str(customer_id)
            coupon.save()
            if coupon.coupon_type == 'Percentage':
                return Response({"status": True, "message": 'Valid Coupon', 'type': 'Percentage', 'percentage_off': coupon.coupon_amt, 'max_amount': coupon.coupon_amt_limit})
            elif coupon.coupon_type == 'Amount':
                return Response({"status": True, "message": 'Valid Coupon', 'type': 'Amount', 'coupon_amount': coupon.coupon_amt, 'min_amount_limit': coupon.coupon_amt_limit})
