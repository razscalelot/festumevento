from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as httpStatus
from rest_framework.permissions import IsAuthenticated
import requests
import json
from .serializers import UserSerializer, UserUpdateProfileSerializer
from . import models, serializers

from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import logout

import api.views
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render

from django.utils.crypto import get_random_string


import math
import random


def getReferralCode():
    ref_code = get_random_string(
        6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    try:
        models.User.objects.get(
            my_refer_code=ref_code
        )
        return getReferralCode()
    except models.User.DoesNotExist:
        return ref_code


def genrateAllUserRefCode():
    users = models.User.objects.all()
    print("init---------------------")
    for user in users:
        user.my_refer_code = getReferralCode()
        print("User " + user.name + " - " + user.my_refer_code)
        user.save()
    print("end---------------------")

# genrateAllUserRefCode()


class UserListView(generics.ListAPIView):
    queryset = models.User.objects.filter(admin__exact=False)
    serializer_class = serializers.UserSerializer


class GetUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fcm_Token = request.GET.get("fcmtoken", None)
        if fcm_Token != None:
            request._user.fcm_token = fcm_Token
            request._user.save()
        serializer = UserSerializer(request._user)
        return Response({
            "status": True,
            "user": serializer.data
        }, status=httpStatus.HTTP_201_CREATED)


    def post(self, request, format=None):
        serializer = UserUpdateProfileSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'status': True, 'msg': "Your profile is updated Successfully."}, status=httpStatus.HTTP_200_OK)
        return Response({'status': False, 'msg': "There is some issue in update."}, status=httpStatus.HTTP_400_BAD_REQUEST)


class UserCreate(APIView):

    def post(self, request, format='json'):
        print('call', request.data)
        if not request.POST._mutable:
            request.POST._mutable = True
        request.data["my_refer_code"] = getReferralCode()
        if request.data.get("refer_code") is None:
            request.data["refer_code"] = ""
        if request.data.get("fcm_token") is None:
            request.data["fcm_token"] = ""
        print('request.data', request.data['confirm_password'])
        serializer = UserSerializer(data=request.data)
        status = False
        verror = None
        try:
            status = serializer.is_valid(raise_exception=True)
        except Exception as error:
            verror = error

        if status:
            user = serializer.save()
            print('user.mobile', user)
            api.views.set_Free_Subscription(user)
            if user:
                return Response({
                    "status": status,
                    "data": serializer.data
                }, status=httpStatus.HTTP_201_CREATED)
            else:
                return Response({
                    "status": status,
                    "data": serializer.data
                }, status=httpStatus.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response(
                {"status": status,
                 "error": verror.detail
                 }, status=httpStatus.HTTP_406_NOT_ACCEPTABLE)


class UserLogin(APIView):
    def post(self, request, format='json'):
        mobile = request.data.get("mobile")
        password = request.data.get("password")
        fcmToken = request.data.get("fcmtoken")
        if mobile is None or password is None:
            return Response({'error': 'Please provide both mobile and password'},
                            status=httpStatus.HTTP_400_BAD_REQUEST)
        user = authenticate(username=mobile, password=password)
        if not user:
            return Response({'error': 'You have entered an invalid mobile number or password.'},
                            status=httpStatus.HTTP_400_BAD_REQUEST)
        if fcmToken is not None:
            user.fcm_token = request.data.get("fcmtoken")
            user.save()
        token, _ = Token.objects.get_or_create(user=user)
        serializer = serializers.TokenSerializer(token)
        # serializer = UserSerializer(user, many=True)

        return Response({"detail": serializer.data},
                        status=httpStatus.HTTP_200_OK)
        # return Response({'error': 'Error while login, Please try again'},
        #              status=httpStatus.HTTP_400_BAD_REQUEST)


class UserLogout(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request.user.auth_token.delete()
        return Response({"status": True, 'detail': "ok"}, status=httpStatus.HTTP_200_OK)


class SendOtp(APIView):
    def post(self, request, **kwargs):
        print('request')
        mobile_number = request.data.get("mobile")
        if mobile_number:
            mobile = str(mobile_number)
            if mobile:
                otp = generateOTP()
                otpRes = send_otp_request(mobile, otp)
                if otpRes["Status"] != "Error":
                    models.OtpLog.objects.create(
                        mobile=mobile,
                        otp=otp,
                        smsKey=otpRes["Details"]
                    )
                    return Response(
                        {
                            "status": True,
                            'smsKey': otpRes["Details"]
                        },
                        status=httpStatus.HTTP_200_OK
                    )
                else:
                    return Response(
                        {
                            "status": False,
                            'error': "Error while sending SMS",
                        },
                        status=httpStatus.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {
                        "status": False,
                        'error': "You are not register with us"
                    },
                    status=httpStatus.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {
                    "status": False,
                    'error': "Invalid mobile number"
                },
                status=httpStatus.HTTP_400_BAD_REQUEST
            )


class VerifyOtp(APIView):
    def post(self, request, format='json'):
        print('call')
        # mobile_number = request.data.get("mobile")
        # key = request.data.get("key")
        otp = request.data.get("otp")

        if otp:
            mobile_number = str(mobile_number)
            # c_user = models.User.objects.filter(mobile__iexact=mobile_number)
            otp_log = models.OtpLog.objects.filter(
                mobile__iexact=mobile_number, smsKey=key, otp=otp)
            if otp_log.exists():
                verify = verify_otp_request(key, otp)
                if verify["Status"] == "Success" and verify["Details"] == "OTP Matched":
                    # cc_user = c_user[0]
                    # if len(cc_user.refer_code) >= 6:
                    #     coin = 10
                    #     try:
                    #         refer_user = models.User.objects.filter(
                    #             my_refer_code=cc_user.refer_code
                    #         )
                    #         if refer_user.count() > 0:
                    #             refer_user = refer_user[0]
                    #             api.views.tranCoin(cc_user, coin, refer_user, cc_user, "LOGIN_REFER", "CREDIT", "", "",
                    #                                "User " + cc_user.name+" refer by " + refer_user.name+" as " + cc_user.role, "", "")
                    #             if cc_user.role == "Organiser":
                    #                 coin = 20
                    #             api.views.tranCoin(refer_user, coin, refer_user, cc_user, "REFERED", "CREDIT", "", "",
                    #                                "User " + cc_user.name+" refer by " + refer_user.name+" as " + cc_user.role, "", "")
                    #     except models.User.DoesNotExist:
                    #         coin = 0
                    # c_user.update(verify=True)
                    return Response(
                        {
                            "status": True,
                            "Details": verify["Details"]
                        }
                    )
                else:
                    return Response(
                        {
                            "status": False,
                            "detail": verify["Details"]
                        },
                        status=httpStatus.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {
                        "status": False,
                        "detail": "You are not register with us"
                    },
                    status=httpStatus.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {
                    "status": False,
                    'detail': "Invalid mobile otp"
                },
                status=httpStatus.HTTP_400_BAD_REQUEST
            )


class VerifyOtpChangePassword(APIView):
    def post(self, request, format='json'):
        mobile_number = request.data.get("mobile")
        key = request.data.get("key")
        otp = request.data.get("otp")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if mobile_number and key and otp and password and confirm_password:
            if password == confirm_password and len(str(password)) >= 8:
                mobile_number = str(mobile_number)
                c_user = models.User.objects.filter(
                    mobile__iexact=mobile_number)
                otp_log = models.OtpLog.objects.filter(
                    mobile__iexact=mobile_number, smsKey=key)
                if c_user.exists() and otp_log.exists():
                    verify = verify_otp_request(key, otp)
                    if verify["Status"] == "Success" and verify["Details"] == "OTP Matched":
                        c_user = c_user[0]
                        c_user.set_password(password)
                        c_user.save()
                        return Response(
                            {
                                "status": True,
                                "Details": "Password Changed"
                            },
                            status=httpStatus.HTTP_200_OK
                        )
                    else:
                        return Response(
                            {
                                "status": False,
                                "error": verify["Detail"]
                            },
                            status=httpStatus.HTTP_400_BAD_REQUEST
                        )
                else:
                    return Response(
                        {
                            "status": False,
                            "error": "You are not register with us"
                        },
                        status=httpStatus.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {
                        "status": False,
                        "error": "confirm password does not match."
                    },
                    status=httpStatus.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {
                    "status": False,
                    'error': "The OTP entered is incorrect."
                },
                status=httpStatus.HTTP_400_BAD_REQUEST
            )

def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP


def send_otp_request(mobile, otp):
    url = "http://2factor.in/API/V1/8f1dd888-03a5-11ea-9fa5-0200cd936042/SMS/" + \
        mobile + "/" + otp
    payload = ""
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.request("GET", url, data=payload, headers=headers)
    return json.loads(response.text)


def verify_otp_request(key, otp):
    url = "http://2factor.in/API/V1/8f1dd888-03a5-11ea-9fa5-0200cd936042/SMS/VERIFY/" + key + "/" + otp
    payload = ""
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.request("GET", url, data=payload, headers=headers)
    return json.loads(response.text)
