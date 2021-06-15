from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.shortcuts import render
from requests.models import Response
from rest_framework.views import APIView
from django.http import Http404
from django.core.signing import Signer
import urllib.request as urllib2
import urllib
from django.db.models import Sum
import uuid
import random
import string
import requests
from hashlib import blake2b
from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework import viewsets, status
from rest_framework.response import Response
from customer.serializers import *
from .serializers import *
from .models import *
from passlib.hash import pbkdf2_sha256
import json
# Create your views here.
from customer.views import generate, send_otp, get_referral_id
from customer.serializers import *
from customer.models import *
from rest_framework.parsers import MultiPartParser, FormParser

class BookingHost(APIView):
    serializer_class = ChargerListSerializer

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        chargers = Charger.objects.all()
        return chargers

    def get(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']
        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):

            try:
                chargers = Charger.objects.filter(
                    charger_host=host_id)

            except:
                return Response({"status": "not found"})

            serializer = ChargerListSerializer(chargers, many=True)
            return Response(serializer.data)
        else:
            return Response({"status": "invalid authkey"})


# profile
class Profile(APIView):
    serializer_class = HostSerialiser

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        host = Host.objects.all()
        return host

    def get(self, request, *args, **kwargs):

        host_id = request.query_params['host_id']

        try:
            host = Host.objects.get(host_id=host_id)
        except Host.DoesNotExist:
            return Response({"status": "not found"})
        serializer = HostSerialiser(host)
        return Response(serializer.data)


class EditProfile(APIView):
    serializer_class = EditHost
    parser_classes = (MultiPartParser, FormParser)

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        host = Host.objects.all()
        return host

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        id = request.query_params['host_id']
        token = request.query_params['authkey']
        try:
            host = Host.objects.get(host_id=id)
        except Host.DoesNotExist:
            return Response({"status": "not found"})
        if host.verifyToken(token):
            try:
                if request.data['host_image']:
                     serializer = EditHost(host, data=request.data)
                else:
                    newdict =request.data.copy()
                    newdict.pop("host_image")
                    serializer = EditHost(host, data=newdict)
                    
            except:
                serializer = EditHost(host, data=request.data)
 
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "invalid authkey"})


#
# appointments


class HostAppointmentList(APIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerialiser
    

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']

        token = request.query_params['authkey']
        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            try:
                appointment = Appointment.objects.filter(
                    app_charger__charger_host=host_id)
            except Charger.DoesNotExist:
                return Response({"status": "host not found"})

            serializer = AppointmentSerialiser(appointment, many=True)
            return Response(serializer.data)

        else:
            return Response({"status": "invalid authkey"})


# charger appointmentList
class ChargerAppointmentList(APIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerialiser

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']

        token = request.query_params['authkey']
        charger_id = request.query_params['charger_id']
        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            try:

                appointment = Appointment.objects.filter(
                    Q(app_charger=charger_id) & Q(app_status='Upcoming'))
            except Appointment.DoesNotExist:
                return Response({"status": "host not found"})
            if appointment:
                serializer = AppointmentSerialiser(appointment, many=True)
                return Response(serializer.data)
            return Response({"status": "no appointment available"})
        else:
            return Response({"status": "invalid authkey"})


class AddCharger(APIView):
    serializer_class = CreateCharger
    parser_classes = (MultiPartParser, FormParser)

    @classmethod
    def get_extra_actions(cls):
        return []

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']

        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            try:
                if request.data["charger_brand_logo"]:
                     serializer = CreateCharger(data=request.data)
                else:
                    newdict =request.data.copy()
                    newdict.pop("charger_brand_logo")
                    serializer = serializer = CreateCharger(data=newdict)
                    
            except:
                serializer = CreateCharger(data=request.data)
            # serializer = CreateCharger(data=request.data)
            if serializer.is_valid():
                print(serializer.data)
                serializer.save()
                return Response({'data': serializer.data})


class EditCharger(APIView):
    serializer_class = EditChargerSerializer
    parser_classes = (MultiPartParser, FormParser)

    @classmethod
    def get_extra_actions(cls):
        return []

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']
        charger_id = request.query_params['charger_id']

        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            charger = Charger.objects.get(charger_id=charger_id)
            serializer = EditChargerSerializer(charger, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
    
    def delete(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']
        charger_id = request.query_params['charger_id']

        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            charger = Charger.objects.get(charger_id=charger_id)
            charger.delete()
            return Response({'status': True, 'message': 'charger deleted'})


class AddSocket(APIView):
    serializer_class = AddSocketSerializer

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        socket = ChargerSocket.objects.all()
        return socket

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']

        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            serializer = AddSocketSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data)


class EditSocket(APIView):
    serializer_class = AddSocketSerializer

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        socket = ChargerSocket.objects.all()
        return socket

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']
        socket_id = request.query_params['socket_id']

        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            socket = ChargerSocket.objects.get(id=socket_id)
            serializer = AddSocketSerializer(socket, data=request.data)
            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']
        socket_id = request.query_params['socket_id']

        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            socket = ChargerSocket.objects.get(id=socket_id)
            socket.delete()
            return Response({'status': True, 'message': 'socket deleted'})


class AddNearby(APIView):
    serializer_class = NearbySerializer
    parser_classes = (MultiPartParser, FormParser)

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        Nearby = Nearby.objects.all()
        return Nearby

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']

        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            serializer = NearbySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data)


class EditNearby(APIView):
    serializer_class = NearbySerializer
    parser_classes = (MultiPartParser, FormParser)

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        nearby = Nearby.objects.all()
        return nearby

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']
        Nearby_id = request.query_params['Nearby_id']

        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            nearby = Nearby.objects.get(id=Nearby_id)
            serializer = NearbySerializer(nearby, data=request.data)
            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']
        Nearby_id = request.query_params['Nearby_id']

        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            nearby = Nearby.objects.get(id=Nearby_id)
            nearby.delete()
            return Response({'status': True, 'message': 'Nearby deleted'})


class AddPhoto(APIView):
    serializer_class = AddPhotosSerializer
    parser_classes = (MultiPartParser, FormParser)

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        photo = Photo.objects.all()
        return photo

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']

        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            serializer = AddPhotosSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data)


class EditPhoto(APIView):
    serializer_class = AddPhotosSerializer
    parser_classes = (MultiPartParser, FormParser)

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        photo = Photo.objects.all()
        return photo

    @csrf_exempt
    # def put(self, request, *args, **kwargs):
    #     host_id = request.query_params['host_id']
    #     token = request.query_params['authkey']
    #     photo_id = request.query_params['photo_id']
    #     try:
    #         host = Host.objects.get(host_id=host_id)
    #     except:
    #         return Response({'message': 'invalid host_id'})
    #     if host.verifyToken(token):
    #         photo = Photo.objects.get(id=photo_id)
    #         serializer = AddPhotosSerializer(photo, data=request.data)
    #         if serializer.is_valid():
    #             serializer.save()
    #         return Response(serializer.data)
    def delete(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']
        photo_id = request.query_params['photo_id']

        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            photo = Photo.objects.get(id=photo_id)
            photo.delete()
            return Response({'status': True, 'message': 'photo deleted'})


# # #
# # # To get, check referal id and update the credits
# # #


class Referal(APIView):
    # queryset = Host.objects.all()
    # serializer_class = CustomerSerialiser

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        host = Host.objects.all()
        return host

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        referalID = request.query_params['referalID']
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']
        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            credit = CreditType.objects.get(credit_name='Refer')
            amt = credit.credit_amt
            host = Host.objects.get(host_id=host_id)
            if host.host_referal == referalID:
                return Response({"status": "Invalid referal ID "})

            try:
                host_refered = Host.objects.get(host_referal=referalID)

            except Host.DoesNotExist:
                return Response({"status": "Invalid referal ID "})
            host.host_credit += amt
            host_refered.host_credit += amt
            host.save()
            host_refered.save()
            credit_detail = Credit.objects.create(
                credit_host=host, credit_type=credit, credit_status=True)
            refered_credit_detail = Credit.objects.create(
                credit_host=host_refered, credit_type=credit, credit_status=True)
            credit_detail.save()
            refered_credit_detail.save()

            return Response({"status": "valid referal ID "})
        else:
            return Response({"status": "invalid authkey"})


# my earnings
class MyEarning(APIView):
    queryset = Appointment.objects.all()
    serializer_class = Bill_Details

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']

        token = request.query_params['authkey']

        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            try:
                bill = Bill_Details.objects.filter(bill_host=host_id)
            except:
                return Response({'message': 'invalid gduithost_id'})
            serializer = BillingViewSerialiser(bill, many=True)
            return Response(serializer.data)


# # otp

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
        message = urllib.parse.quote("CHARZER HOST OTP is: ")
        Secret_hash = b'asd2c1fsa25s'
        h = blake2b(digest_size=16, person=Secret_hash)
        sender = "CHARZER"
        if mobiles:
            phone = str(mobiles)
            mobile = str(mobiles).encode(encoding='UTF-8')
            h.update(mobile)

            try:
                host = Host.objects.get(host_phone=phone)
            except Host.DoesNotExist:
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
                            'detail': 'Sending otp error. Limit Exceeded. Please Contact customer support'
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
                    host = Host.objects.get(host_phone=phone)
                    token = old.otp_session_id
                    host.host_token = pbkdf2_sha256.encrypt(token)
                    host.save()
                    old.delete()
                    # host = hosts.objects.get(host_phone=phone)
                    return Response({
                        'authKey': token,
                        'host id': host.host_id,
                        'status': True,
                        'detail': 'Host logged in',

                    })
                except:
                    token = pbkdf2_sha256.encrypt(old.otp_session_id)
                    referralID = get_referral_id(old.phone)

                    host_data = {
                        "host_name": "User Name",
                        "host_email": "",
                        "host_phone": old.phone,
                        "host_address": "",
                        "host_credit": 0.0,
                        "host_referal": referralID,
                        "host_token": token

                    }
                    serializer = HostSerialiser(data=host_data)
                    if serializer.is_valid():
                        otp_session_id = old.otp_session_id
                        old.save()
                        serializer.save()
                        old.delete()
                        host = Host.objects.get(host_phone=phone)
                        return Response({
                            'authkey': otp_session_id,
                            'host id': host.host_id,
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


class LogOut(generics.ListAPIView):

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        host = Host.objects.all()
        return host

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']
        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            host.host_token = "**"
            host.save()
            return Response({
                'status': True,
                'detail': 'Logged out successfully'
            })
        else:
            return Response({"status": "invalid authkey"})


class HostNotificationList(APIView):
    serializer_class = HostNotificationSerializer

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        notification = HostNotification.objects.all()
        return notification

    def get(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']
        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            try:
                notification = HostNotification.objects.filter(N_Host=host)
            except:
                return Response({"status": "host not found"})
            if notification:
                serializer = HostNotificationSerializer(
                    notification, many=True)
                return Response(serializer.data)
            return Response({"status": "no notification available"})
        else:
            return Response({"status": "invalid authkey"})

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        serializer = HostNotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)


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
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']
        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):

            try:
                charger = Charger.objects.get(charger_id=charger_id)
            except Charger.DoesNotExist:
                return Response({"status": "charger not found"})
            serializer = ChargeringStationSerialiser(charger)
            return Response(serializer.data)
        else:
            return Response({
                "message": "invalid authkey"
            })


class Sockets(generics.ListAPIView):
    serializer_class = SocketTypeSerializer

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        sockets = SocketType.objects.all()
        return sockets

    def get(self, request, *args, **kwargs):
        sockets = SocketType.objects.all()
        serializer = SocketTypeSerializer(sockets, many=True)
        return Response(serializer.data)


class CreditTypeView(generics.ListAPIView):
    serializer_class = CreditTypeSerializer

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        creditTypes = CreditType.objects.all()
        return creditTypes

    def get(self, request, *args, **kwargs):
        creditTypes = CreditType.objects.all()
        serializer = CreditTypeSerializer(creditTypes, many=True)
        return Response(serializer.data)


class UpdateHostCredit(APIView):
    # serializer_class = HostSerialiser

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        host = Host.objects.all()
        return host

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        id = request.query_params['host_id']
        token = request.query_params['authkey']
        credit = request.query_params['credit']
        credit = float(credit)

        try:
            host = Host.objects.get(host_id=id)
        except Host.DoesNotExist:
            return Response({"status": "not found"})
        if host.verifyToken(token):
            new_credit = host.host_credit + credit
            if new_credit < 0:
                return Response({"status": False, "message": 'the credit can not be less than zero'})
            host.host_credit = new_credit
            host.save()
            return Response({"status": True, "host_credit": host.host_credit})
        else:
            return Response({"status": "invalid authkey"})


class TotalChargerEarning(APIView):

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        charger = Charger.objects.all()
        return charger

    def get(self, request, *args, **kwargs):
        host_id = request.query_params['host_id']
        token = request.query_params['authkey']
        charger_id = request.query_params['charger_id']
        try:
            host = Host.objects.get(host_id=host_id)
        except:
            return Response({'message': 'invalid host_id'})

        if host.verifyToken(token):
            try:
                charger = Charger.objects.get(charger_id=charger_id)
                chargerTotal = Bill_Details.objects.filter(
                    bill_app__app_charger=charger).aggregate(
                    total=Sum('bill_amount'))
            except:
                return Response({"status": "host not found"})
            if chargerTotal:
                return Response(chargerTotal)
            return Response({"status": "no bill available"})
        else:
            return Response({"status": "invalid authkey"})

import io
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser


@csrf_exempt
def testz(request):
    # charger_d = request.query_params['charger_id']
    # return HttpResponse(charger_d)
    json_data  = request.body
    stream = io.BytesIO(json_data)
    pythondata = JSONParser().parse(stream)
    n=pythondata["charger_id"]
    return HttpResponse(n)

@csrf_exempt
def testzb(request):
    return render(request, "host/formz.html")