
from multiprocessing import context

from requests import request
import api.FCMmanager as fcm
from django.core.mail import send_mail
# from twilio.rest import Client
from .environ import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from django.db import connection
import email
import csv
import threading
from api.chatterbot import bot
import copy
import imp
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializars import *
from .models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models import F, Q
from django.db.models import Prefetch
from datetime import datetime, date
from django.db.models.functions import Radians, Power, Sin, Cos, ATan2, Sqrt, Radians, Now
from django.core import serializers
from django.db.models import Sum
import api.sms
from decimal import Decimal
import base64
import os
import subprocess
import uuid
from django.conf import settings
from pyfcm import FCMNotification
import math
import api.razorpayx
from itertools import chain
from rest_framework.parsers import JSONParser
from festumevento.settings import CHATTERBOT
import io
import csv
import pandas as pd
from rest_framework import generics
from currency_converter import CurrencyConverter
from itertools import chain
# from api.chatterbot import bot

# Create your views here.


def get_Subscription_user(user_instance):
    sub = SubscriptionTransaction.objects.filter(
        user=user_instance,
        is_active=True,
        payment_status='Payed',
        used_post__lt=F('no_of_post'),
        used_days__lt=F('max_days'),
        start_date__lte=date.today().strftime('%Y-%m-%d'),
        end_date__gte=date.today().strftime('%Y-%m-%d')
    ).order_by('-timestamp')
    print(sub.query)
    return sub


def set_Free_Subscription(user_instance):
    print('user_instance', user_instance)
    request = {"subscription_id": "5", "our_payment_id": "admin",
               "user_phone": user_instance.mobile}
    serializer = SubscriptionTransactionSerializer(data=request)
    if serializer.is_valid():
        serializer.save()
    else:
        raise Exception("Invalid Data")


class Payment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data["user_phone"] = request._user.mobile
        serializer = PaymentTransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": False, "detail": serializer.data}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            pt_int = PaymentTransaction.objects.get(
                our_payment_id=request.data["our_payment_id"])
            pt_int.status = request.data["status"]
            pt_int.save()
            serializer = PaymentTransactionSerializer(pt_int)
            return Response({"status": True, "detail": "Updated"}, status=status.HTTP_201_CREATED)
        except Exception as err:
            return Response({"status": True, "detail": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class UserSubscription(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data["user_phone"] = request._user.mobile
        serializer = SubscriptionTransactionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            smsreturn = api.sms.SubscriptionSMS(
                request._user.mobile, request._user.name, serializer.data["price"], serializer.data["name"])
            return Response({"status": True, "detail": serializer.data, 'sms': str(smsreturn)}, status=status.HTTP_201_CREATED)
        return Response({"status": False, "detail": serializer.data}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):

        try:
            # mobile = request.query_params["user_phone"]
            user_instance = request._user
            # sub = get_Subscription_user(user_instance)
            sub = SubscriptionTransaction.objects.filter(
                # user=user_instance,
                is_active=True,
                payment_status='Payed',
                used_post__lt=F('no_of_post'),
                used_days__lt=F('max_days'),
                start_date__lte=date.today().strftime('%Y-%m-%d'),
                end_date__gte=date.today().strftime('%Y-%m-%d')
            ).order_by('-timestamp')
            serializer = SubscriptionTransactionSerializer(sub, many=True)
            return Response({"status": True, "detail": serializer.data}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"status": False, "error": "No details found", "detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionMasterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.data.get("id") == None:
            try:
                sub = SubscriptionMaster.objects.filter(
                    is_active=True
                ).order_by("-price")
                serializer = SubscriptionMasterSerializer(sub, many=True)
                return Response({"status": True, "detail": serializer.data}, status=status.HTTP_200_OK)
            except Exception as err:
                return Response({"status": False, "detail": str(err)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                sub = SubscriptionMaster.objects.filter(
                    is_active=True, id=request.data.get("id")
                ).order_by("-price")
                serializer = SubscriptionMasterSerializer(sub, many=True)
                return Response({"status": True, "detail": serializer.data}, status=status.HTTP_200_OK)
            except Exception as err:
                return Response({"status": False, "detail": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        if request.data.get("id") == None:
            serializer = SubscriptionMasterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            subscription = SubscriptionMaster.objects.get(
                id=request.data["id"])
            subscription.name = request.data["name"]
            subscription.price = request.data["price"]
            subscription.no_of_post = request.data["no_of_post"]
            subscription.max_days = request.data["max_days"]
            subscription.validity_days = request.data["validity_days"]
            subscription.is_active = request.data["is_active"]
            subscription.save()

        return Response({"status": True}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        sub = SubscriptionMaster.objects.get(id=request.data.get("id"))
        sub.is_active = False
        sub.save()
        return Response({"delete": True, "message": "Deleted Successfully."}, status=status.HTTP_200_OK)


class OrgEvents(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=0):
        if id != 0:
            event = Event.objects.filter(
                is_active=True, user=request.user, id=id).order_by('-id')
        else:
            event = Event.objects.filter(
                is_active=True, user=request.user).order_by('-id')

        serializer = EventSerializer(event, many=True)

        return Response(
            {
                "events": serializer.data,

            },
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, id):
        event = Event.objects.get(id=id, user=request.user)
        event.is_active = False
        event.save()
        return Response(
            {
                "delete": True,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        if not request.POST._mutable:
            request.POST._mutable = True
        request.data['is_active'] = True
        request.data["user"] = request._user.id
        serializer = EventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        discount = Discounts.objects.all()
        for dis in discount:
            OrgDiscounts.objects.create(
                event_id_id=serializer.data['id'], user_id_id=request._user.id, discount_type=dis.discount_type, discount=dis.discount)
        return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)

    def put(self, request, id):
        event = Event.objects.get(id=id)
        event.name = request.data["name"]
        event.event_type = request.data["event_type"]
        event.event_category = request.data["event_category"]
        event.is_other = request.data["is_other"]
        event.is_active = True
        event.save()
        return Response({"status": True}, status=status.HTTP_201_CREATED)


class SetEvent(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.POST._mutable:
            request.POST._mutable = True
        vstatus = False
        verror = None

        request.data["user"] = request._user.id

        try:
            event = Event.objects.get(
                name=request.data["name"],
                event_type=request.data["event_type"],
                user=request._user)
        except Event.DoesNotExist:
            event = None

        if event == None:
            serializer = EventSerializer(data=request.data)
            try:
                vstatus = serializer.is_valid(raise_exception=True)
            except Exception as error:
                verror = error
        else:
            vstatus = True
            serializer = EventSerializer(event)
            return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)

        if vstatus:
            serializer.save()
            return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"status": vstatus,
                 "error": str(verror)
                 }, status=status.HTTP_406_NOT_ACCEPTABLE)

    def get(self, request, id=0):
        # limit = int(request.GET.get('limit', 5))
        # page = int(request.GET.get('page', 1))

        if id != 0:
            sub = EventRegistration.objects.filter(
                is_active=True, event__user=request.user.id, id=id).order_by('-id') #.order_by('start_date')
        else:
            sub = EventRegistration.objects.filter(
                is_active=True,
                event__user=request.user.id
            ).order_by('-id') #.order_by('start_date')

        # total = sub.count()
        # start = (page - 1) * limit
        # end = page * limit

        # serializer = EventRegistrationSerializer2(sub[start:end], many=True)
        serializer = EventRegistrationSerializer2(sub, many=True)
        data = serializer.data

        # for d in data:
        #     for o in d['discount_id']:
        #         print('o', o['orgdiscount'])
        # discount = OrgDiscounts.objects.filter(orgdiscountsId=d['discount_id'])
        # print('discount', discount)

        # print('data', data[-1]['discount_id'])
        for event in data:
            id = int(event["id"])
            ratings = CommentsAndRating.objects.filter(
                occasion=id,
                is_active=True
            ).order_by('-timestamp')[:1]
            ratings = CommentsAndRatingSerializer(ratings, many=True).data
            if len(ratings) > 0:
                event["rating"] = ratings[0]['avg_rating']
                event["user_rating"] = ratings[0]['avg_user_rating']
            else:
                event["rating"] = 0.0
                event["user_rating"] = 0.0
            invo = Invoice.objects.filter(event_reg=id)
            if(invo.count() >= 1):
                event["invoice_status"] = invo[0].status
            else:
                event["invoice_status"] = ""

        shops = Shop.objects.filter(
            user=request.user,
            is_active=True
        )

        shopSerializer = ShopSerializer(shops, many=True)
        shopSerializerData = shopSerializer.data

        for shop in shopSerializerData:
            local = LocalOffer.objects.filter(
                is_active=True,
                shop=shop["id"]
            )
            offerSer = LocalOfferSerializer2(local, many=True)
            offerData = offerSer.data
            for offer in offerData:
                ratings = CommentsAndRating.objects.filter(
                    offer=offer["id"],
                    is_active=True
                ).order_by('-timestamp')[:1]
                ratings = CommentsAndRatingSerializer(ratings, many=True).data
                if len(ratings) > 0:
                    offer["rating"] = ratings[0]['avg_rating']
                    offer["user_rating"] = ratings[0]['avg_user_rating']
                else:
                    offer["rating"] = 0.0
                    offer["user_rating"] = 0.0
            shop["offers"] = offerData

        return Response(
            {
                # "total": total,
                # "page": page,
                # "last_page": math.ceil(total / limit),
                # "next": 'next',
                # "previous": 'previous',
                "events": data,
                "local": shopSerializerData

            },
            status=status.HTTP_201_CREATED
        )


class EventRegister(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print('request.data', request.data)
        vstatus = False
        verror = None
        serializer = EventRegistrationSerializer(data=request.data)
        print('serializer', serializer)

        try:
            vstatus = serializer.is_valid(raise_exception=True)
            print('vstatus', vstatus)
        except Exception as error:
            verror = error

        if vstatus:
            model_obj = serializer.save() 
            print('serializer.data', serializer.data)           
            return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"status": vstatus,
                 #  "error": str(verror)
                 "error": serializer.errors
                 }, status=status.HTTP_406_NOT_ACCEPTABLE)

    def put(self, request, id=0):
        vstatus = False
        verror = None
        event = EventRegistration.objects.get(id=id)
        serializer = EventRegistrationSerializer(event, data=request.data)

        try:
            vstatus = serializer.is_valid(raise_exception=True)
        except Exception as error:
            verror = error

        if vstatus:
            model_obj = serializer.save()
            return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"status": vstatus,
                 #  "error": str(verror)
                 "error": serializer.errors
                 }, status=status.HTTP_406_NOT_ACCEPTABLE)

    def get(self, request):
        sub = EventRegistration.objects.filter(
            is_active=True,
        )

        serializer = EventRegistrationSerializer(sub, many=True)

        return Response(
            {
                "detial": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class DiscountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=0):
        user = request._user.id
        if id != 0:
            discount = Discounts.objects.filter(discountsId=id)
        else:
            discount = Discounts.objects.all()
        discount_serializer = DiscountSerializers(discount, many=True)
        return JsonResponse({
            'message': "Data fetch Successfully",
            'data': discount_serializer.data,
            'isSuccess': True
        }, status=200)

    def post(self, request):
        vstatus = False
        verror = None
        serializer = DiscountSerializers(data=request.data)

        try:
            vstatus = serializer.is_valid(raise_exception=True)
        except Exception as error:
            verror = error

        if vstatus:
            model_obj = serializer.save()
            return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"status": vstatus,
                 #  "error": str(verror)
                 "error": serializer.errors
                 }, status=status.HTTP_406_NOT_ACCEPTABLE)

    def put(self, request, id):
        discount = Discounts.objects.get(discountsId=id)
        discount_serializer = DiscountSerializers(discount, data=request.data)
        if discount_serializer.is_valid():
            discount_serializer.save()
            return JsonResponse({
                'message': "Updated Successfully",
                'data': discount_serializer.data,
                'isSuccess': True
            }, status=200)
        return JsonResponse({
            'message': "Insertion Faild",
            'data': discount_serializer.errors,
            'isSuccess': False
        }, status=200)


class OrgDiscountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=0):
        user = request._user.id
        if id != 0:
            discount = OrgDiscounts.objects.filter(
                id=id, user_id=user, event_id=int(request.GET.get('event_id')))
        else:
            discount = OrgDiscounts.objects.filter(user_id=user, event_id=int(request.GET.get('event_id')))
        discount_serializer = OrgDiscountSerializers(discount, many=True)
        return JsonResponse({
            'message': "Data fetch Successfully",
            'data': discount_serializer.data,
            'isSuccess': True
        }, status=200)

    # def post(self, request):
    #     vstatus = False
    #     verror = None
    #     _id = request.data['orgequipmentdiscounts_id']
    #     exist = OrgEquipment.objects.get(orgequipmentdiscounts_id=_id)
    #     if exist:
    #         serializer = OrgEquipmentSerializers(exist, data=request.data)
    #     else:
    #         serializer = OrgEquipmentSerializers(data=request.data)

    #     try:
    #         vstatus = serializer.is_valid(raise_exception=True)
    #     except Exception as error:
    #         verror = error

    #     if vstatus:
    #         model_obj = serializer.save()
    #         return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(
    #             {"status": vstatus,
    #              #  "error": str(verror)
    #              "error": serializer.errors
    #              }, status=status.HTTP_406_NOT_ACCEPTABLE)

    def put(self, request, id):        
        user = request._user.id
        odiscount = OrgDiscounts.objects.get(id=id, event_id=int(request.GET.get('event_id')), user_id=user)            
        odiscount.equipment_id_id = request.data['equipment_id']
        odiscount.discount = request.data['discount']
        if odiscount:
            odiscount.save()
            discount_serializer = OrgDiscountSerializers(odiscount)
            if (request.data['equipment_id'] != None or '') and (odiscount.discount_type == 'discount_on_equipment_or_item'):
                u = OrgEquipmentId.objects.filter(orgdiscount_id__user_id=request.user.id)
                u.delete()
                for i in request.data['equipment_id']:
                    OrgEquipmentId.objects.update_or_create(orgdiscount_id_id=discount_serializer.data['id'], equipment_id_id=i)
                serializer = OrgDiscountSerializers(odiscount)
                return JsonResponse({
                    'message': "Updated Successfully",
                    'data': serializer.data,
                    'isSuccess': True
                }, status=200)            
            return JsonResponse({
                    'message': "Updated Successfully",
                    'data': discount_serializer.data,
                    'isSuccess': True
                }, status=200)
        return JsonResponse({
            'message': "Insertion Faild",
            'data': discount_serializer.errors,
            'isSuccess': False
        }, status=200)


class EventCompanyDetailsView(APIView):

    def get(self, request):
        print('request.data', request.GET.get('event_reg', 0))
        companydetail = EventCompanyDetails.objects.filter(
            event_reg=request.GET.get('event_reg', 0))
        serializer = EventCompanyDetailsSerializer(companydetail, many=True)
        return JsonResponse({
            'message': "Data fetch Successfully",
            'data': serializer.data,
            'isSuccess': True
        }, status=200)

    def post(self, request):
        vstatus = False
        verror = None
        serializer = EventCompanyDetailsSerializer(data=request.data)

        try:
            vstatus = serializer.is_valid(raise_exception=True)
        except Exception as error:
            verror = error

        if vstatus:
            serializer.save()
            return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"status": vstatus,
                 "error": str(verror)
                 }, status=status.HTTP_406_NOT_ACCEPTABLE)


class EventCompanyImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        vstatus = False
        verror = None
        serializer = EventCompanyImageSerializer(data=request.data)

        try:
            vstatus = serializer.is_valid(raise_exception=True)
        except Exception as error:
            verror = error

        if vstatus:
            serializer.save()
            return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"status": vstatus,
                 "error": str(verror)
                 }, status=status.HTTP_406_NOT_ACCEPTABLE)

    def delete(self, request):

        images = EventCompanyImage.objects.get(
            id=str(request.GET.get('id', 0))
        )

        images.image.delete()
        images.delete()

        return Response(
            {
                "detail": True,
            },
            status=status.HTTP_201_CREATED
        )


class EventCompanyVideoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        vstatus = False
        verror = None
        serializer = EventCompanyVideoSerializer(data=request.data)

        try:
            vstatus = serializer.is_valid(raise_exception=True)
        except Exception as error:
            verror = error

        if vstatus:
            serializer.save()
            return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"status": vstatus,
                 "error": str(verror)
                 }, status=status.HTTP_406_NOT_ACCEPTABLE)

    def delete(self, request):

        videos = EventCompanyVideo.objects.get(
            id=str(request.GET.get('id', 0))
        )

        videos.video.delete()
        videos.delete()

        return Response(
            {
                "detail": True,
            },
            status=status.HTTP_201_CREATED
        )


class EventPersonalDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        vstatus = False
        verror = None
        serializer = EventPersonalDetailsSerializer(data=request.data)

        try:
            vstatus = serializer.is_valid(raise_exception=True)
        except Exception as error:
            verror = error

        if vstatus:
            serializer.save()
            return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"status": vstatus,
                 "error": str(verror)
                 }, status=status.HTTP_406_NOT_ACCEPTABLE)


class EventPriceMatrix(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        vstatus = False
        verror = None
        serializer = PriceMatrixSerializer(data=request.data)

        try:
            vstatus = serializer.is_valid(raise_exception=True)
        except Exception as error:
            verror = error

        if vstatus:
            serializer.save()
            return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"status": vstatus,
                 "error": str(verror)
                 }, status=status.HTTP_406_NOT_ACCEPTABLE)

    def get(self, request):

        price = PriceMatrix.objects.filter(
            event_reg=request.GET.get('event_reg', 0)
        ).order_by('number')

        serializer = PriceMatrixSerializer(price, many=True)

        return Response(
            {
                "detail": serializer.data,
            },
            status=status.HTTP_201_CREATED
        )


class LocalOfferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # try:
        user_instance = request._user
        # sub = get_Subscription_user(user_instance)
        if(1 > 0):
            sub = SubscriptionTransaction.objects.filter(id=26)[0]
            vstatus = False
            verror = None
            request.data["subscription"] = sub.id
            serializer = LocalOfferSerializer(data=request.data)

            # try:
            vstatus = serializer.is_valid(raise_exception=True)
            # except Exception as error:
            #     verror = error

            if vstatus:
                v_user_post_left = sub.no_of_post - sub.used_post
                v_user_days_left = sub.max_days - sub.used_days
                sub.used_post = sub.used_post+1
                sub.used_days = sub.used_days + int(request.data["no_of_days"])

                # if(sub.used_post > sub.no_of_post or sub.used_days > sub.max_days):
                #     vstatus = False
                #     verror = ValueError(
                #         "Local offer exceeds the active subscription. No of posts left are "+str(v_user_post_left)
                #         +" and no of days left are "+str(v_user_days_left))

            if vstatus:
                model_obj = serializer.save()

                sub.save()
                return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"status": vstatus,  "error": str(verror)}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"status": False, "error": "No active subcription found"}, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as error:
        #     return Response({"status": False, "error": "No details found "+str(error), "detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class OfferProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        vstatus = False
        verror = None
        serializer = Offer_ProductSerializer(data=request.data)
        vstatus = serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)

    def get(self, request):
        product = Offer_Product.objects.filter(
            local_offer=request.GET.get("offer", 0)
        )
        serializer = Offer_ProductSerializer(product, many=True)
        productData = serializer.data
        for pro in productData:
            offers = Offer_Discount.objects.filter(
                product=pro["id"]
            )
            offerSer = Offer_DiscountSerializer(offers, many=True)
            pro["offers"] = offerSer.data

            images = LocalOffer_Image.objects.filter(
                product=pro["id"]
            )
            imageSer = LocalOfferImageSerializer(images, many=True)
            pro["images"] = imageSer.data

        return Response({"status": True, "detail": productData}, status=status.HTTP_201_CREATED)


class OfferDiscountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = Offer_DiscountSerializer(data=request.data)
        vstatus = serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)


class ShopCategoryView(APIView):

    def get(self, request, id=0):
        if id != 0:
            category = ShopCategory.objects.filter(id=id, is_active=True)
        else:
            category = ShopCategory.objects.filter(is_active=True)
        categorySerializer = ShopCategorySerializer(category, many=True)
        return Response({
            'detail': categorySerializer.data
        }, status=status.HTTP_200_OK)


class EventImages(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        vstatus = False
        verror = None
        serializer = EventImageSerializer(data=request.data)

        try:
            vstatus = serializer.is_valid(raise_exception=True)
        except Exception as error:
            verror = error

        if vstatus:
            serializer.save()
            return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"status": vstatus,
                 "error": str(verror)
                 }, status=status.HTTP_406_NOT_ACCEPTABLE)

    def get(self, request):

        images = EventImage.objects.filter(
            event_reg=request.GET.get('event_reg', 0)
        ).order_by('timestamp')

        serializer = EventImageSerializer(images, many=True)

        return Response(
            {
                "detail": serializer.data,
            },
            status=status.HTTP_201_CREATED
        )

    def delete(self, request):

        images = EventImage.objects.get(
            id=str(request.GET.get('id', 0))
        )

        images.image.delete()
        images.delete()

        return Response(
            {
                "detail": True,
            },
            status=status.HTTP_201_CREATED
        )


class EventVideos(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        vstatus = False
        verror = None
        serializer = EventVideoSerializer(data=request.data)

        try:
            vstatus = serializer.is_valid(raise_exception=True)
        except Exception as error:
            verror = error

        if vstatus:
            serializer.save()
            return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"status": vstatus,
                 "error": str(verror)
                 }, status=status.HTTP_406_NOT_ACCEPTABLE)

    def get(self, request):

        videos = EventVideo.objects.filter(
            event_reg=request.GET.get('event_reg', 0)
        ).order_by('timestamp')

        serializer = EventVideoSerializer(videos, many=True)

        return Response(
            {
                "detail": serializer.data,
            },
            status=status.HTTP_201_CREATED
        )

    def delete(self, request):

        video = EventVideo.objects.get(
            id=str(request.GET.get('id', 0))
        )

        video.video.delete()
        video.delete()

        return Response(
            {
                "detail": True,
            },
            status=status.HTTP_201_CREATED
        )


class EventGallery(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request._user.id
        print('user ', user)
        images = EventImage.objects.filter(event_reg__event_id__user_id=user)
        image_serializer = EventImageSerializer(images, many=True)
        videos = EventVideo.objects.filter(event_reg__event_id__user_id=user)
        video_serializer = EventVideoSerializer(videos, many=True)
        gallery = list(chain(image_serializer.data, video_serializer.data))

        return Response(
            {
                "gallery": gallery
            },
            status=status.HTTP_201_CREATED
        )


class LocalOfferImages(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        vstatus = False
        verror = None
        serializer = LocalOfferImageSerializer(data=request.data)
        vstatus = serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)

    def get(self, request):

        images = LocalOffer_Image.objects.filter(
            local_offer=request.GET.get('offer', 0)
        ).order_by('timestamp')

        serializer = LocalOfferImageSerializer(images, many=True)

        return Response(
            {
                "detail": serializer.data,
            },
            status=status.HTTP_201_CREATED
        )


class LocalOfferVideos(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        vstatus = False
        verror = None
        serializer = LocalOfferVideoSerializer(data=request.data)

        try:
            vstatus = serializer.is_valid(raise_exception=True)
        except Exception as error:
            verror = error

        if vstatus:
            serializer.save()
            return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"status": vstatus,
                 "error": str(verror)
                 }, status=status.HTTP_406_NOT_ACCEPTABLE)

    def get(self, request):

        images = LocalOffer_Video.objects.filter(
            local_offer=request.GET.get('offer', 0)
        ).order_by('timestamp')

        serializer = LocalOfferVideoSerializer(images, many=True)

        return Response(
            {
                "detail": serializer.data,
            },
            status=status.HTTP_201_CREATED
        )


class ConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        images = Config.objects.filter(
            key=request.GET.get('key', 0)
        )

        serializer = ConfigSerializer(images, many=True)

        return Response(
            {
                "detail": serializer.data,
            },
            status=status.HTTP_201_CREATED
        )


class ShopView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.POST._mutable:
            request.POST._mutable = True

        request.data["user"] = request._user.id
        if not str.isdigit(str(request.data["category"])):
            cat = None
            cat = ShopCategory()
            cat.category_name = request.data["category"]
            cat.is_active = True
            cat.save()
            request.data["category"] = cat.id

        # request.data["category"] = cat
        if request.data.get("id") == None:
            serializer = ShopSerializer2(data=request.data)
        else:
            shop = Shop.objects.get(id=request.data["id"])
            serializer = ShopSerializer2(shop, data=request.data)
        # serializer = ShopSerializer(data=request.data)
        vstatus = False
        # try:
        vstatus = serializer.is_valid(raise_exception=True)
        # except Exception as error:
        #     verror = error
        serializer.save()
        return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
        # else:
        #     return Response(
        #         {"status": vstatus,
        #          "error": verror
        #          }
        #         , status=status.HTTP_406_NOT_ACCEPTABLE)

    def get(self, request):
        shops = Shop.objects.filter(
            user=request._user,
            is_active=True
        )
        serializer = ShopSerializer(shops, many=True)
        return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        shops = Shop.objects.filter(
            user=request._user,
            is_active=True,
            id=request.data["id"]
        )
        if shops.count() > 0:
            shop = shops[0]
            shop.is_active = False
            shop.save()
        return Response({"status": True}, status=status.HTTP_201_CREATED)


class StateView(APIView):

    def get(self, request):
        state = State.objects.all()
        serializer = StateSerializer(state, many=True)
        statelist = serializer.data
        for st in statelist:
            # print(st["state"])
            city = City.objects.filter(state__id=st["id"])
            Cityserializer = CitySerializer(city, many=True)
            st["citys"] = Cityserializer.data
        return Response(
            {
                "detail": statelist,
            },
            status=status.HTTP_201_CREATED
        )


class UserAttendee(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        attendees = Attendee.objects.filter(
            event_reg__id=request.GET.get('event', 0),
            event_reg__event__user=request._user
        )

        serializer = AttendeeSerializer2(attendees, many=True)

        data = serializer.data

        for i in data:
            tickets = Ticket.objects.filter(
                attendee__id=i["id"]
            )
            tickets_s = TicketSerializer(tickets, many=True)
            i["tickets"] = tickets_s.data

        return Response(
            {
                "status": True,
                "detail": data
            },
            status=status.HTTP_201_CREATED
        )


class UserLocalBooking(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        localBooking = LocalOfferBooking.objects.filter(
            local__id=request.GET.get('local', 0),
            user=request._user
        ).order_by("rank_number")

        serializer = LocalOfferBookingSerializer3(localBooking, many=True)

        data = serializer.data

        for i in data:
            bookingOffer = LocalOfferBookingProducts.objects.filter(
                booking=i["id"],
            )
            i["products"] = LocalOfferBookingProductsSerializer(
                bookingOffer, many=True).data

        return Response(
            {
                "status": True,
                "detail": data,
                # "query" : str(localBooking.query)
            },
            status=status.HTTP_201_CREATED
        )


# User Side API
lat_1km = 0.00900
lng_1km = 0.00355
distance = 50


class UserGetOccasion(APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            occasion_id = request.GET.get('occasion', "0")
            events = EventRegistration.objects.filter(
                id=occasion_id,
                is_verify=True, is_active=True, status__icontains='SUBMIT'
            ).order_by('-end_date', '-start_date')
            serializer = EventRegistrationSerializer2(events, many=True)
            print(events.query)

            data = serializer.data
            for i in data:
                ratings = CommentsAndRating.objects.filter(
                    occasion=i["id"],
                    is_active=True
                ).order_by('-timestamp')[:1]
                ratings = CommentsAndRatingSerializer(ratings, many=True).data
                if len(ratings) > 0:
                    i["rating"] = ratings[0]['avg_rating']
                    i["user_rating"] = ratings[0]['avg_user_rating']
                else:
                    i["rating"] = 0.0
                    i["user_rating"] = 0.0
                try:
                    wishlist = WishlistOccation.objects.filter(
                        occasion=i["id"],
                        user=request._user
                    )
                    if wishlist.count() > 0:
                        i["is_wishlist"] = wishlist[0].is_active
                    else:
                        i["is_wishlist"] = False
                except:
                    i["is_wishlist"] = False

            return Response(
                {
                    "status": True,
                    "detial": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as error:
            return Response(
                {
                    "status": False,
                    "detial": str(error)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserEventsView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            search = request.GET.get('search', "")
            print('get search', search)
            current_lat = float(request.GET.get('lat', 0))
            print('get current_lat', current_lat)
            current_long = float(request.GET.get('long', 0))
            print('get current_long', current_long)
            city = request.GET.get('city', "")
            print('get city', city)
            pincode = request.GET.get('pincode', "")
            print('get pincode', pincode)
            min_lat = current_lat - (lat_1km * distance)
            max_lat = current_lat + (lat_1km * distance)

            min_lng = current_long - (lng_1km * distance)
            max_lng = current_long + (lng_1km * distance)

            start = request.GET.get('start')
            print('start', start)
            end = request.GET.get('end')

            today = datetime.today()

            if search:
                events = EventRegistration.objects.filter(
                    Q(latitude__gte=min_lat, latitude__lte=max_lat, longitude__gte=min_lng, longitude__lte=max_lng) |
                    Q(city__icontains=search) | Q(
                        pincode__icontains=search) | Q(address__icontains=search)
                    | Q(event__name__icontains=search) | Q(description__icontains=search),
                    # Q(start_date__gte=today) | Q(end_date__gte=today),
                    is_verify=True, is_active=True)
                print('search event', events)

            elif city:
                print('city', city)
                events = EventRegistration.objects.filter(
                    Q(city__icontains=city), is_verify=True, is_active=True)
                print('city event', events)

            elif pincode:
                print('pinecode', pincode)
                events = EventRegistration.objects.filter(
                    Q(pincode__icontains=pincode))

            elif start or end:
                print('call')
                print('date', start)
                events = EventRegistration.objects.filter(
                    Q(start_date__gte=int(start)) | Q(end_date__gte=end))
                print('date event', events)

            elif min_lat != '' or max_lat != '' or min_lng != '' or min_lng != '':
                print('lng', min_lat, max_lat, min_lng, min_lng)
                events = EventRegistration.objects.filter(
                    Q(latitude__gte=min_lat, latitude__lte=max_lat, longitude__gte=min_lng, longitude__lte=max_lng))

            print('event', events)

            serializer = EventRegistrationSerializer2(events, many=True)

            print('serializer.data', serializer.data)

            data = serializer.data
            for i in data:
                price = PriceMatrix.objects.filter(
                    event_reg=i["id"]
                ).order_by('number')
                priceserializer = PriceMatrixSerializer(price, many=True)
                i["price_matric"] = priceserializer.data

            return Response(
                {
                    "status": True,
                    "detail": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as error:
            return Response(
                {
                    "status": False,
                    "detail": str(error)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserGetOffer(APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            offer = request.GET.get('offer', "00")
            locaOffer = LocalOffer.objects.filter(
                id=offer,
                is_verify=True, is_active=True, status__icontains='SUBMIT'
            ).order_by('-start_date')
            print(locaOffer.query)
            serializer = LocalOfferSerializerForUser(locaOffer, many=True)

            data = serializer.data
            for i in data:
                category = ShopCategory.objects.filter(
                    id=i["shop"]["category"]
                )
                if(category.count() > 0):
                    i["shop"]["category"] = ShopCategorySerializer(
                        category[0]).data
                products = Offer_Product.objects.filter(
                    local_offer=i["id"]
                ).order_by('id')
                ratings = CommentsAndRating.objects.filter(
                    offer=i["id"],
                    is_active=True
                ).order_by('-timestamp')[:1]
                ratings = CommentsAndRatingSerializer(ratings, many=True).data
                if len(ratings) > 0:
                    i["rating"] = ratings[0]['avg_rating']
                    i["user_rating"] = ratings[0]['avg_user_rating']
                else:
                    i["rating"] = 0.0
                    i["user_rating"] = 0.0

                try:
                    wishlist = WishlistOffer.objects.filter(
                        offer=i["id"],
                        user=request._user
                    )
                    if wishlist.count() > 0:
                        i["is_wishlist"] = wishlist[0].is_active
                    else:
                        i["is_wishlist"] = False
                except:
                    i["is_wishlist"] = False
                if products.count() >= 1:
                    lastProduct = products[products.count() - 1]
                    offers = Offer_Discount.objects.filter(
                        product=lastProduct.id
                    )
                    if offers.count() >= 1:
                        lastOffer = offers[offers.count()-1]
                        discount = ""
                        price = str(int(float(lastOffer.price)))
                        if lastOffer.discount_type == "PERCENTAGE":
                            discount = "Upto "+price + "% off"
                        elif lastOffer.discount_type == "AMOUNT":
                            discount = "Upto ₹"+price + " off"
                        i["offer"] = discount

            return Response(
                {
                    "status": True,
                    "detial": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as error:
            return Response(
                {
                    "status": False,
                    "detial": str(error)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR

            )


class UserLocalOffer(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            search = request.GET.get('search', "$")
            current_lat = float(request.GET.get('lat', 0))
            current_long = float(request.GET.get('long', 0))
            city = request.GET.get('city', 0)
            pincode = request.GET.get('pincode', 0)
            min_lat = current_lat - (lat_1km * distance)
            max_lat = current_lat + (lat_1km * distance)

            min_lng = current_long - (lng_1km * distance)
            max_lng = current_long + (lng_1km * distance)
            start = int(request.GET.get('start', 0))
            end = start + 15

            today = datetime.today()

            if search == "$":
                # locaOffer = LocalOffer.objects.filter(
                #         Q(latitude__gte=min_lat,latitude__lte=max_lat,longitude__gte=min_lng,longitude__lte=max_lng)
                #         |
                #         Q(city__icontains = city)
                #         |
                #         Q(pincode__icontains = pincode),
                #         Q(start_date__gte = today),
                #         is_verify= True,is_active= True,status__icontains = 'SUBMIT'
                #         ).order_by('-start_date')[start:end]

                locaOffer = LocalOffer.objects.filter(
                    end_date__gte=today,
                    is_verify=True, is_active=True, status__icontains='SUBMIT'
                ).order_by('-start_date')[start:end]
            else:
                locaOffer = LocalOffer.objects.filter(
                    Q(offer_name__icontains=search) |
                    Q(shop__shop_name__icontains=search) |
                    Q(shop__category__category_name__icontains=search),
                    is_verify=True, is_active=True, status__icontains='SUBMIT',
                    end_date__gte=today,
                ).order_by('-start_date')[start:end]
            serializer = LocalOfferSerializerForUser(locaOffer, many=True)

            data = serializer.data
            for i in data:
                category = ShopCategory.objects.filter(
                    id=i["shop"]["category"]
                )
                if(category.count() > 0):
                    i["shop"]["category"] = ShopCategorySerializer(
                        category[0]).data
                products = Offer_Product.objects.filter(
                    local_offer=i["id"]
                ).order_by('id')
                if products.count() >= 1:
                    lastProduct = products[products.count() - 1]
                    offers = Offer_Discount.objects.filter(
                        product=lastProduct.id
                    )
                    if offers.count() >= 1:
                        lastOffer = offers[offers.count()-1]
                        discount = ""
                        price = str(int(float(lastOffer.price)))
                        if lastOffer.discount_type == "PERCENTAGE":
                            discount = "Upto "+price + "% off"
                        elif lastOffer.discount_type == "AMOUNT":
                            discount = "Upto ₹"+price + " off"
                        i["offer"] = discount

            return Response(
                {
                    "status": True,
                    "detial": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as error:
            return Response(
                {
                    "status": False,
                    "detial": str(error)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR

            )


def getBooking(user, local):
    try:
        booking = LocalOfferBooking.objects.get(
            user=user,
            local=local,
        )
    except LocalOfferBooking.DoesNotExist:
        booking = None

    if(booking != None):
        serializer = LocalOfferBookingSerializer(booking, many=False)
        bookingData = serializer.data
        offerProduct = LocalOfferBookingProducts.objects.filter(
            booking=bookingData["id"]
        )
        ser = LocalOfferBookingProductsSerializer(offerProduct, many=True)
        bookingData["products"] = ser.data
        return bookingData
    return None


class BookLocal(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = getBooking(request._user, request.data["local"])

            if(data != None):
                return Response(
                    {"status": False,
                     "error": "Already Booked",
                     "detail": data
                     }, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                selectedProduct = request.data["products"]

                products = Offer_Product.objects.filter(
                    local_offer=request.data["local"],
                    id__in=selectedProduct
                )

                localOffer = LocalOffer.objects.get(
                    id=request.data["local"]
                )

                availedOfferList = []
                notAvailedOfferList = []
                for product in products:
                    offers = Offer_Discount.objects.filter(
                        product=product.id,
                        is_active=True
                    )
                    for offer in offers:
                        if offer.number == -1 or offer.sold + 1 <= offer.number:
                            availedOfferList.append({
                                "product": product,
                                "offer": offer,
                                "rank": offer.sold + 1
                            })
                            break
                        else:
                            notAvailedOfferList.append({
                                "product": product.id,
                                "offer": offer.id,
                                "rank": offer.sold + 1
                            })
                count = 0
                if len(availedOfferList) > 0:
                    time_threshold = datetime.now()
                    all_booking = LocalOfferBooking.objects.filter(
                        local=request.data["local"],
                        expire__lte=time_threshold
                    ).count()

                    d = timedelta(hours=24)
                    Expdate = datetime.now() + d
                    last_date = datetime(
                        localOffer.end_date.year, localOffer.end_date.month, localOffer.end_date.day)
                    if Expdate >= last_date:
                        Expdate = last_date

                    book = LocalOfferBooking()
                    book.local = localOffer
                    book.rank_number = all_booking+1
                    book.user = request._user
                    book.expire = Expdate
                    book.is_avail = False
                    book.avail_datetime = datetime.now()
                    book.save(force_insert=True)
                    book.ticket_number = book.pk + 10000000
                    book.save()

                    for availOffer in availedOfferList:
                        offerBook = LocalOfferBookingProducts()
                        offerBook.rank_number = availOffer["rank"]
                        offerBook.booking = book
                        offerBook.offer = availOffer["offer"]
                        offerBook.product = availOffer["product"]
                        availOffer["offer"].sold = availOffer["offer"].sold+1
                        count = count + 1
                        offerBook.save(force_insert=True)
                        availOffer["offer"].save()
                        availOffer["offer"] = availOffer["offer"].id
                        availOffer["product"] = availOffer["product"].id

                localOffer.sold = localOffer.sold + count
                localOffer.save()
                data = getBooking(request._user, request.data["local"])
                return Response(
                    {
                        "status": True,
                        "availed": availedOfferList,
                        "notAvailed": notAvailedOfferList,
                        "detail": data
                    },
                    status=status.HTTP_201_CREATED)

                # ---------------------------------------------
                # time_threshold = datetime.now()
                # all_booking = LocalOfferBooking.objects.filter(
                #     local = request.data["local"],
                #     expire__lte = time_threshold
                # ).count()
                # local =  LocalOffer.objects.get(
                #     pk =  request.data["local"]
                # )

                # last_date = local.start_date + timedelta(days=local.no_of_days)

                # if all_booking > local.quantity :
                #     return Response(
                #     {"status": False,
                #     "error": "Booking Full",
                #     }
                #     , status=status.HTTP_406_NOT_ACCEPTABLE)
                # else:
                #     d = timedelta(hours= 24)
                #     date = datetime.now()  + d
                #     last_date = datetime(last_date.year, last_date.month, last_date.day)
                #     #date = date.date()
                #     if date >= last_date:
                #         date = last_date

                #     book = LocalOfferBooking()
                #     book.local = local
                #     book.rank_number = all_booking+1
                #     book.user = request._user
                #     book.expire = date
                #     book.is_avail = False
                #     book.avail_datetime = datetime.now()

                #     offers = offer_first.objects.filter(
                #         local_offer = local
                #     )
                #     selected_offer = None
                #     for offer in offers:
                #         if book.rank_number <= offer.number:
                #             selected_offer = offer
                #             break

                #     book.offer = selected_offer
                #     book.save(force_insert=True)
                #     book.ticket_number = book.pk+ 10000000
                #     book.save()
                #     local.sold = all_booking
                #     smsvalue = api.sms.ReferanceSMS(
                #         request._user.mobile,
                #         request._user.name,
                #         str(selected_offer.number)+("% " if selected_offer.discount_type == "PERCENTAGE" else "₹"),
                #         local.product_name,
                #         local.event.name,
                #         book.ticket_number
                #     )
                #     serializer = LocalOfferBookingSerializer(book)

                #     return Response(
                #         {
                #             "status": True,
                #             "detial":serializer.data,
                #             "sms": str(smsvalue)
                #         },
                #         status=status.HTTP_201_CREATED)

        except Exception as error:
            return Response(
                {"status": False,
                 "error": str(error),
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def seatPriceCalcutater(occasion, seats):
    total_amount = 0
    canBookingDone = True
    total_count = 0

    for seat in seats:
        try:
            seatObj = SeatingArrangementBooking.objects.get(
                occasion_id=occasion,
                id=seat['seat_booking_id']
            )
            total_booking_count = seatObj.total_booking_count
            if total_booking_count == None:
                total_booking_count = 0
            total_seat = total_booking_count + seat['no_of_seat']
            if total_seat > seatObj.no_of_seat:
                seat['is_error'] = True
                seat['error_code'] = 1001
                seat['no_of_seat'] = 0
                seat['amount'] = 0
                seat['total_seat'] = 0
                canBookingDone = canBookingDone and False
            else:
                seat['is_error'] = False
                seat['error_code'] = 0000
                seat['amount'] = seat['no_of_seat'] * seatObj.price_per_seat
                seat['total_seat'] = total_seat
                total_amount = total_amount + seat['amount']
                total_count = total_count + total_seat
        except:
            seat['is_error'] = True
            seat['error_code'] = 1002
            seat['no_of_seat'] = 0
            seat['amount'] = 0
            seat['total_seat'] = 0
            canBookingDone = canBookingDone and False
    return {
        "total_amount":  total_amount,
        "seats": seats,
        "can_booking_done": canBookingDone,
        "total_count": total_count,
    }


class PriceCountEvent(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            occasion = int(str(request.data["occasion"]))
            seats = request.data["seats"]

            data = seatPriceCalcutater(occasion, seats)
            print('data', data)
            return Response(
                {"status": True,
                 "total_amount": data["total_amount"],
                 "seats": data["seats"],
                 "can_booking_done": data['can_booking_done']
                 }, status=status.HTTP_200_OK)

        except Exception as error:
            return Response(
                {"status": False,
                 "error": str(error),
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def post(self, request):
    #     try:
    #         count = int(str(request.data["count"]))
    #         event = request.data["event"]

    #         prices = PriceMatrix.objects.filter(
    #             event_reg=event
    #         ).order_by('-number')

    #         alocated_prices = []
    #         tCount = count

    #         for price in prices:
    #             result = divmod(tCount, price.number)
    #             if(result[1] >= 0):
    #                 for i in range(0, result[0], 1):
    #                     alocated_prices.append(price)
    #                 tCount = result[1]
    #             else:
    #                 continue

    #         Totalprice = 0
    #         alocated_prices_s = []
    #         for price in alocated_prices:
    #             Totalprice = Totalprice + price.price
    #             alocated_prices_s.append(PriceMatrixSerializer(price).data)

    #         all_booking = Attendee.objects.filter(
    #             event_reg=event,
    #         ).aggregate(Sum('ticket_count'))['ticket_count__sum']
    #         if all_booking == None:
    #             all_booking = 0
    #         all_booking = all_booking + int(str(request.data["count"]))

    #         event_a = EventRegistration.objects.get(
    #             pk=request.data["event"]
    #         )
    #         if all_booking > event_a.capacity:
    #             return Response(
    #                 {"status": False,
    #                  "error": "Booking Full",
    #                  }, status=status.HTTP_406_NOT_ACCEPTABLE)
    #         else:
    #             return Response(
    #                 {"status": True,
    #                  "price": str(Totalprice),
    #                  "detail": alocated_prices_s
    #                  }, status=status.HTTP_200_OK)

    #     except Exception as error:
    #         return Response(
    #             {"status": False,
    #              "error": str(error),
    #              }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookEvent(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            event = EventRegistration.objects.get(
                pk=request.data["event"]
            )

            payment = PaymentTransaction.objects.get(
                our_payment_id=request.data["our_payment_id"]
            )

            all_booking = Attendee.objects.filter(
                event_reg=request.data["event"],
            ).aggregate(Sum('ticket_count'))['ticket_count__sum']
            if all_booking == None:
                all_booking = 0
            all_booking = all_booking + int(str(request.data["count"]))

            if all_booking >= event.capacity:
                return Response(
                    {"status": False,
                     "error": "Booking Full",
                     }, status=status.HTTP_406_NOT_ACCEPTABLE)

            event.sold = all_booking
            event.save()
            book = Attendee()
            book.user = request._user
            book.event_reg = event
            book.book_on = datetime.now()
            book.total_amount = request.data["amount"]
            book.payment = payment
            book.status = request.data["status"]
            book.ticket_count = request.data["count"]
            book.is_avail = False
            book.avail_datetime = datetime.now()

            book.save(force_insert=True)
            book.ticket_number = book.pk + 10000000
            book.save()

            for price in request.data["price_detail"]:
                ticket = Ticket()
                ticket.attendee = book
                ticket.price_matrix = PriceMatrix.objects.get(pk=price["id"])
                ticket.amount = price["price"]
                ticket.status = request.data["status"]
                ticket.number = price["number"]
                ticket.save()

            serializer = AttendeeSerializer(book)

            smsstatus = api.sms.TicketSMS(request._user.mobile,
                                          request._user.name,
                                          book.ticket_number,
                                          book.total_amount,
                                          event.event.name)

            return Response(
                {
                    "status": True,
                    "detial": serializer.data,
                    "sms": smsstatus
                },
                status=status.HTTP_201_CREATED)

        except Exception as error:
            return Response(
                {"status": False,
                 "error": str(error),
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserBooking(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        event = Attendee.objects.filter(
            user=request._user
        ).order_by("-book_on")

        eas = AttendeeSerializer(event, many=True)

        local = LocalOfferBooking.objects.filter(
            user=request._user
        ).order_by("-expire")

        lob = LocalOfferBookingSerializer(local, many=True)
        lobData = lob.data
        for l in lobData:
            category = ShopCategory.objects.get(
                id=l["local"]["shop"]["category"]
            )
            ser = ShopCategorySerializer(category)
            l["local"]["shop"]["category"] = ser.data
            offerProduct = LocalOfferBookingProducts.objects.filter(
                booking=l["id"]
            )
            ser = LocalOfferBookingProductsSerializer(offerProduct, many=True)
            l["products"] = ser.data

        return Response(
            {
                "status": True,
                "event": eas.data,
                "local": lob.data
            },
            status=status.HTTP_201_CREATED
        )


class ValidateScan(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            option = request.data["type"]
            data = {}
            if option == "Event":
                eat = Attendee.objects.get(
                    ticket_number=request.data["ticket_number"],
                    event_reg__id=request.data["event"],
                    event_reg__event__user=request._user
                )
                data = AttendeeSerializer2(eat).data
            elif option == "LocalOffer":
                eat = LocalOfferBooking.objects.get(
                    ticket_number=request.data["ticket_number"],
                    local__id=request.data["event"],
                    user=request._user
                )
                # print(eat.query)
                data = LocalOfferBookingSerializer3(eat).data
                bookingOffer = LocalOfferBookingProducts.objects.filter(
                    booking=data["id"],
                )
                data["products"] = LocalOfferBookingProductsSerializer(
                    bookingOffer, many=True).data
            else:
                data = {}

            return Response({"status": True,
                             "detail": data}, status=status.HTTP_200_OK)

        except Exception as error:
            return Response({"status": False,
                             "detail": "Ticket does not belong to the event"}, status=status.HTTP_406_NOT_ACCEPTABLE)


class CheckInView(APIView):
    def get(self, request):
        checkListData = Attendee.objects.all()
        checkList = AttendeeSerializer(checkListData, many=True)
        return Response(checkList.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            option = request.data["type"]
            if option == "Event":
                eat = Attendee.objects.get(
                    ticket_number=request.data["ticket_number"],
                    event_reg__id=request.data["event"],
                    event_reg__event__user=request._user
                )
                eat.is_avail = True
                eat.avail_datetime = datetime.now()
                eat.save()
            elif option == "LocalOffer":
                eat = LocalOfferBooking.objects.get(
                    ticket_number=request.data["ticket_number"],
                    local__id=request.data["event"],
                    user=request._user
                )
                eat.is_avail = True
                eat.avail_datetime = datetime.now()
                eat.save()
            return Response({"status": True,
                             "detail": "done"}, status=status.HTTP_200_OK)

        except Exception as error:
            return Response({"status": False,
                             "detail": "Ticket does not belong to the event"}, status=status.HTTP_406_NOT_ACCEPTABLE)


class InvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        invo = Invoice.objects.filter(event_reg=request.GET.get('event', "0"))
        serializer = InvoiceSerializer(invo, many=True)
        return Response({"status": True, "detail": serializer.data}, status=status.HTTP_200_OK)


class VideoAndImages(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):

        today = datetime.today()
        images = EventImage.objects.filter(
            Q(event_reg__start_date__gte=today) | Q(
                event_reg__end_date__gte=today),
            event_reg__is_verify=True, event_reg__is_active=True, event_reg__status__icontains='SUBMIT'
        ).order_by('timestamp')

        image_serializer = SocialEventImageSerializer(images, many=True)
        imagesdata = image_serializer.data
        for img in imagesdata:
            img["type"] = "IMG"
            img['detail_type'] = "event"
            price = PriceMatrix.objects.filter(
                event_reg=img["event_reg"]["id"]
            ).order_by('number')
            priceserializer = PriceMatrixSerializer(price, many=True)
            img["event_reg"]["price_matric"] = priceserializer.data

        videos = EventVideo.objects.filter(
            Q(event_reg__start_date__gte=today) | Q(
                event_reg__end_date__gte=today),
            event_reg__is_verify=True, event_reg__is_active=True, event_reg__status__icontains='SUBMIT'
        ).order_by('timestamp')

        video_serializer = SocialEventVideoSerializer(videos, many=True)
        videosdata = video_serializer.data
        for vid in videosdata:
            vid["type"] = "VID"
            vid['detail_type'] = "event"
            price = PriceMatrix.objects.filter(
                event_reg=img["event_reg"]["id"]
            ).order_by('number')
            priceserializer = PriceMatrixSerializer(price, many=True)
            vid["event_reg"]["price_matric"] = priceserializer.data

        offer_image = LocalOffer_Image.objects.filter(
            Q(product__local_offer__start_date__lte=today),
            Q(product__local_offer__end_date__gte=today),
            product__local_offer__is_verify=True, product__local_offer__is_active=True, product__local_offer__status__icontains='SUBMIT'
        ).order_by('timestamp')

        offer_image_serializer = SocialLocalOfferImageSerializer(
            offer_image, many=True)
        offer_image_data = offer_image_serializer.data
        for i in offer_image_data:
            i["type"] = "IMG"
            i['detail_type'] = "offer"
            product = Offer_Product.objects.get(
                id=i["product"]
            )
            localOffer = LocalOffer.objects.get(
                id=product.local_offer.id
            )
            i["local_offer"] = LocalOfferSerializerForUser(localOffer).data
            products = Offer_Product.objects.filter(
                local_offer=i["local_offer"]["id"]
            ).order_by('id')
            if products.count() >= 1:
                lastProduct = products[products.count() - 1]
                offers = Offer_Discount.objects.filter(
                    product=lastProduct.id
                )
                if offers.count() >= 1:
                    lastOffer = offers[offers.count()-1]
                    discount = ""
                    price = str(int(float(lastOffer.price)))
                    if lastOffer.discount_type == "PERCENTAGE":
                        discount = "Upto "+price + "% off"
                    elif lastOffer.discount_type == "AMOUNT":
                        discount = "Upto ₹"+price + " off"
                    i["local_offer"]["offer"] = discount
            category = ShopCategory.objects.filter(
                id=i["local_offer"]["shop"]["category"]
            )
            if(category.count() > 0):
                i["local_offer"]["shop"]["category"] = ShopCategorySerializer(
                    category[0]).data

        offer_videos = LocalOffer_Video.objects.filter(
            Q(local_offer__start_date__lte=today),
            Q(local_offer__end_date__gte=today),
            local_offer__is_verify=True, local_offer__is_active=True, local_offer__status__icontains='SUBMIT'
        ).order_by('timestamp')

        offer_video_serializer = SocialLocalOfferVideoSerializer(
            offer_videos, many=True)
        offer_video_data = offer_video_serializer.data
        for i in offer_video_data:
            i["type"] = "VID"
            i['detail_type'] = "offer"
            category = ShopCategory.objects.filter(
                id=i["local_offer"]["shop"]["category"]
            )
            if(category.count() > 0):
                i["local_offer"]["shop"]["category"] = ShopCategorySerializer(
                    category[0]).data
            products = Offer_Product.objects.filter(
                local_offer=i["local_offer"]["id"]
            ).order_by('id')
            if products.count() >= 1:
                lastProduct = products[products.count() - 1]
                offers = Offer_Discount.objects.filter(
                    product=lastProduct.id
                )
                if offers.count() >= 1:
                    lastOffer = offers[offers.count()-1]
                    discount = ""
                    price = str(int(float(lastOffer.price)))
                    if lastOffer.discount_type == "PERCENTAGE":
                        discount = "Upto "+price + "% off"
                    elif lastOffer.discount_type == "AMOUNT":
                        discount = "Upto ₹"+price + " off"
                    i["local_offer"]["offer"] = discount

        return Response(
            {
                "images": imagesdata,
                "videos": videosdata,
                "offer_images": offer_image_data,
                "offer_videos": offer_video_data
            },
            status=status.HTTP_201_CREATED
        )


class ComplainView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        vdata = copy.copy(request.data)
        vdata["user"] = request._user.id
        serializers = ComplainSerializer(data=vdata)

        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response({"status": True, "detail": serializers.data}, status=status.HTTP_201_CREATED)


class GenerateBill(APIView):

    def get(self, request):
        today = date.today()
        lastdate = today - timedelta(days=10)

        events = EventRegistration.objects.filter(
            end_date=lastdate
        )
        gst_rate = Decimal(Config.objects.get(key='gst_rate').value)
        commission_rate = Decimal(
            Config.objects.get(key='commission_rate').value)
        our_gst = Config.objects.get(key='gst_no').value
        print(str(gst_rate))
        print(str(commission_rate))
        bills = []
        for event in events.iterator():
            invo = Invoice.objects.filter(event_reg=event)
            if invo.count() <= 0:
                attendees = Attendee.objects.filter(
                    event_reg=event
                )
                gross_amount = 0
                print("----------Event start--------------")
                print("Event Name " + event.event.name)
                for attendee in attendees.iterator():
                    gross_amount += attendee.total_amount
                    print("attendee " + str(attendee.total_amount))

                commission_amount = (commission_rate/100) * gross_amount
                gst_amount = (gst_rate/100) * commission_amount
                net_amount = gross_amount - commission_amount - gst_amount

                gst_no = ""
                bank = UserBankDetail.objects.filter(
                    user=event.event.user, is_active=True)
                if bank.count() > 0:
                    gst_no = bank.first().gst_number

                invoice = Invoice()
                invoice.gst_no_org = gst_no
                invoice.gst_no_our = our_gst
                invoice.gross_amount = gross_amount
                invoice.trans_date = datetime.today()
                invoice.gst_rate = gst_rate
                invoice.gst_amount = gst_amount
                invoice.commission_rate = commission_rate
                invoice.commission_amount = commission_amount
                invoice.net_amount = net_amount
                invoice.status = "invoice generated"
                invoice.user = event.event.user
                invoice.event_reg = event
                invoice.save()
                invoice.invoice_no = str(invoice.pk+1000000)
                invoice.save()

                print("gross_amount " + str(gross_amount))
                print("commission_amount " + str(commission_amount))
                print("gst_amount " + str(gst_amount))
                print("net_amount " + str(net_amount))
                print("gst_no " + str(gst_no))
                print("----------Event End--------------")

                iss = InvoiceSerializer(invoice)
                bills.append(iss.data)

        return Response({
            'lastdate': lastdate,
            'bills': len(bills)
        }, status=status.HTTP_200_OK)


# Poster Service
class PosterCategoryView(APIView):

    def get(self, request):
        ps = PosterCategory.objects.filter(
            is_active=True
        )
        data = PosterCategorySerializer(ps, many=True).data
        return Response({"status": True, "data": data})

    def post(self, request):

        if request.data.get("id") == None:
            vstatus = False
            verror = None
            serializer = PosterCategorySerializer(data=request.data)

            try:
                vstatus = serializer.is_valid(raise_exception=True)
            except Exception as error:
                verror = error

            if vstatus:
                serializer.save()
                return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"status": vstatus,
                     "error": str(verror)
                     }, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            poster = PosterCategory.objects.get(id=request.data["id"])
            poster.category_name = request.data["category_name"]
            poster.is_active = request.data["is_active"]
            poster.save()
            return Response({"status": True, "message": "Updated Successfully."}, status=status.HTTP_201_CREATED)


class PosterByCategoryView(APIView):

    def get(self, request):
        start = int(request.GET.get('start', "0"))
        count = int(request.GET.get('count', "10"))
        categor_id = request.GET.get('categor_id', 0)
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        days = float(request.GET.get('days', 0))

        posters = PosterMaster.objects.filter(
            category=categor_id,
            is_active=True
        )[start:start+count]

        postersData = PosterMasterSerializer(posters, many=True).data

        for poster in postersData:
            discount = PosterPriceCategoryDiscount.objects.filter(
                price_categorty=poster["price_categorty"]["id"],
                is_active=True,
                day__lte=days
            ).order_by('-day')[:1]
            discount = discount[0]
            finalPrice = 0.0
            grossPrice = float(poster["price_categorty"]["price"]) * days
            if discount.discount_type == 'PERCENTAGE':
                finalPrice = grossPrice - \
                    (grossPrice * (float(discount.discount)))
            elif discount.discount_type == 'AMOUNT':
                finalPrice = grossPrice - float(discount.discount)
            else:
                finalPrice = grossPrice
            singleCoinValue = 0
            try:

                conConfig = Config.objects.filter(
                    key="SingleCoinValue"
                )
                if conConfig.count() > 0:
                    singleCoinValue = int(conConfig[0].value)
                else:
                    singleCoinValue = 0
            except:
                singleCoinValue = 0
            poster["coin_price"] = math.ceil(finalPrice*singleCoinValue)
            poster["final_price"] = finalPrice
            poster["discount"] = discount.discount
            poster["price_discount_type"] = discount.discount_type
            poster["discount_day"] = discount.day
            poster["gross_price"] = grossPrice

        return Response({"status": True, "data": postersData})


class PosterValueChangeView(APIView):

    def post(self, request):
        svg = request.data["svg"]
        changeAmount = request.data["amount"]
        changeType = request.data["type"]
        changeText = request.data["text"]
        cmd = request.data["cmd"]
        directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        directoryMedia = directory + "\\media\\buy\\poster\\temp"
        file = open(directory+"/"+svg, 'r')
        data = file.read()
        data = str(data)
        data = data.replace("$Amount$", changeAmount)
        data = data.replace("$type$", changeType)
        data = data.replace("$text$", changeText)
        name = "temp_"+str(uuid.uuid4())+".svg"
        nameOutput = "temp_"+str(uuid.uuid4())+".jpg"
        f = open(directoryMedia+"\\"+name, "w+", encoding='utf-8')
        f.write(data)
        f.close()
        cmd = "svgexport " + directoryMedia+"/"+name + \
            " " + directoryMedia+"/"+nameOutput+" 80"
        p = subprocess.call([cmd], shell=True)
        # p=subprocess.call(['svgexport'directoryMedia+"\\"+name,directoryMedia+"\\"+nameOutput,"80"], shell=True)
        os.remove(directoryMedia+"/"+name)
        encoded = ""
        if cmd == "temp":
            encoded = base64.b64encode(
                open(directoryMedia+"\\"+nameOutput, "rb").read()).decode('ascii')
            os.remove(directoryMedia + "\\" + nameOutput)
        elif cmd == "select":
            encoded = directoryMedia+"\\"+nameOutput
        return Response({"status": True, "data": encoded})


class PosterTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.POST._mutable:
            request.POST._mutable = True

        request.data["user"] = request._user.id
        serializersPT = None
        try:
            pt = PosterTransaction.objects.get(id=request.data["id"])
            serializersPT = PosterTransactionSerializer(pt, data=request.data)
        except:
            serializersPT = PosterTransactionSerializer(data=request.data)

        vstatus = serializersPT.is_valid(raise_exception=True)
        # if(request.data["id"] == None or request.data["id"] == ""):
        serializersPT.save()
        # else:
        #    serializersPT.update()
        data = serializersPT.data
        posterTran = PosterTransaction.objects.get(id=data["id"])
        posterTran.our_payment_id = data["id"] + 10000000000
        data["our_payment_id"] = posterTran.our_payment_id
        posterTran.save()

        return Response({"status": True, "detail": data}, status=status.HTTP_201_CREATED)


class PosterTransactionUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        posterTran = PosterTransaction.objects.get(id=request.data["pt_id"])
        posterTran.status = request.data["pt_status"]
        posterTran.razorpay_order_id = request.data["razorpay_order_id"]
        posterTran.razorpay_payment_id = request.data["razorpay_payment_id"]

        offer = LocalOffer.objects.filter(id=posterTran.local.id)
        offer.update(status=request.data["order_status"])
        posterTran.save()
        return Response({"status": True, "detail": "Done"}, status=status.HTTP_201_CREATED)


class PosterTransactionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        value = request.GET.get("ofid")
        posterTran = PosterTransaction.objects.get(local=value)
        ser = PosterTransactionSerializer(posterTran)
        return Response({"status": True, "detail": ser.data}, status=status.HTTP_201_CREATED)


class AdvertisementMasterView(APIView):

    def get(self, request):
        place = request.GET.get("place", "")
        ads = AdvertisementMaster.objects.filter(
            start_date_time__lte=datetime.now(),
            end_date_time__gte=datetime.now(),
            is_active=True,
            app_place=place
        ).order_by('rank')
        ser = AdvertisementMasterSerializer(ads, many=True)

        return Response({"status": True, "detail": ser.data, "ad_second": Config.objects.get(key='ad_second').value}, status=status.HTTP_201_CREATED)


class AdClickView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ad_id = request.GET.get("ad_id", 0)
        ad_summary = None
        ad = None
        try:
            ad_summary = AdTransactionSummary.objects.get(
                ad=ad_id
            )
            ad = ad_summary.ad
        except Exception as err:
            ad = AdvertisementMaster.objects.get(id=ad_id)
            ad_summary = AdTransactionSummary()
            ad_summary.count = 0
            ad_summary.ad = ad

        ad_summary.count = ad_summary.count + 1
        ad_summary.last_use = datetime.now()
        ad_summary.save()

        ad_detail = AdTransactionDetail()
        ad_detail.ad = ad
        ad_detail.user = request._user
        ad_detail.save()
        return Response({"status": True, "detail": "done", }, status=status.HTTP_201_CREATED)


class CoinSummaryLedgerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = {}
        try:
            summary = CoinSummaryLedger.objects.get(user=request._user)
            summarySer = CoinSummaryLedgerSerializer(summary)
            data = summarySer.data
            singleCoinValue = 0
            try:

                conConfig = Config.objects.filter(
                    key="SingleCoinValue"
                )
                if conConfig.count() > 0:
                    singleCoinValue = int(conConfig[0].value)
                else:
                    singleCoinValue = 0
            except:
                singleCoinValue = 0
            data["single_coin_value"] = singleCoinValue
        except CoinLedger.DoesNotExist:
            data = {}
        return Response({"status": True, "detail": data}, status=status.HTTP_201_CREATED)


class CoinLedgerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        id = request.GET.get("id", None)
        data = {}
        if id == None:
            ledgers = CoinLedger.objects.filter(
                user=request._user
            ).order_by('-trans_timestamp')
            data = CoinLedgerSerializer(ledgers, many=True).data
        else:
            ledger = CoinLedger.objects.get(
                user=request._user,
                pk=id
            )
            data = CoinLedgerSerializer(ledger).data
        return Response({"status": True, "detail": data}, status=status.HTTP_201_CREATED)


class CoinTransaction(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        coin = request.data["coin"]
        ltype = request.data["ltype"]
        ttype = request.data["ttype"]
        statement = request.data["statement"]
        tranID = request.data["tranId"]
        tranCoin(request._user, coin, request._user, request._user,
                 ltype, ttype, "", "", statement, tranID, "")
        return Response({"status": True, "detail": "Ok"}, status=status.HTTP_201_CREATED)


class TransactionUserCoin(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sendUser = request._user
        receiverUserID = request.data["receiver_user_id"]
        receiverUser = User.objects.get(id=receiverUserID)
        coin = int(request.data["coin"])
        ltype = "COIN_SEND"
        ttype = "DEBIT"
        statement = "User "+sendUser.name+" has transfer coin " + \
            str(coin) + " to user " + receiverUser.name
        tranID = "LocalOfferId:" + \
            request.data["local_offer_id"]+"," + \
            "ticketNo:"+request.data["ticket_no"]
        tranCoin(request._user, coin, sendUser, receiverUser,
                 ltype, ttype, "", "", statement, tranID, "")
        ltype = "COIN_RECEIVE"
        ttype = "CREDIT"
        statement = "User " + receiverUser.name+" has received coin " + \
            str(coin) + " from user " + sendUser.name
        notifyStatement = "while shopping at " + request.data["shop_name"]
        tranCoin(receiverUser, coin, receiverUser, sendUser, ltype,
                 ttype, "", "", statement, tranID, notifyStatement)
        return Response({"status": True, "detail": "Ok"}, status=status.HTTP_201_CREATED)


class IsToEnableCoinSystem(APIView):
    def get(self, request):
        coinDetail = {
            "totalCoin": 0,
            "MaxCoin": 0,
            "isEnableCoinSystem": False
        }
        conConfig = Config.objects.filter(
            key="CoinMaster"
        )
        if conConfig.count() > 0:
            conConfig = conConfig[0]
            coinDetail = {
                "totalCoin": int(conConfig.value),
                "MaxCoin": int(conConfig.subvalue),
                "isEnableCoinSystem": int(conConfig.value) < int(conConfig.subvalue)
            }
            if(int(conConfig.subvalue)) == -1:
                coinDetail["isEnableCoinSystem"] = True
        else:
            coinDetail["isEnableCoinSystem"] = True

        return Response(coinDetail, status=status.HTTP_201_CREATED)


class testNotification(APIView):
    def get(self, request):
        rid = request.GET.get("rid", None)
        if rid != None:
            data_message = {
                "coin": 20,
                "type": "LOGIN_REFER",
                "tran_type": "DEBIT",
                "total_coin": 320,
            }
            push_service = FCMNotification(api_key=settings.FCM_SERVER_API_KEY)
            registration_id = rid
            message_title = "Wow! congratulations"
            message_body = "You have won " + \
                str(20)+" F-Coin by refering to " + " Abhishek D" + "."
            result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                       message_body=message_body, data_message=data_message, click_action="FLUTTER_NOTIFICATION_CLICK")


def tranCoin(_user, coin, receive_from, receive_on_behalf,
             type, tranType, redeem_upi, redeem_status, remark, transcation_number, notifyStatement):
    try:
        cl = CoinLedger()
        cl.user = _user
        cl.number_of_coin = coin
        cl.receive_from = receive_from
        cl.receive_on_behalf = receive_on_behalf
        cl.type = type
        cl.trans_type = tranType
        cl.redeem_upi = redeem_upi
        cl.redeem_status = redeem_status
        cl.remark = remark
        cl.transcation_number = transcation_number
        cl.save()

        coinSummaryLedger = None
        try:
            coinSummaryLedger = CoinSummaryLedger.objects.get(user=_user)
        except CoinSummaryLedger.DoesNotExist:
            coinSummaryLedger = CoinSummaryLedger()
            coinSummaryLedger.user = _user
            coinSummaryLedger.total_coin = 0
            coinSummaryLedger.redeem_coin = 0
            coinSummaryLedger.redeem_amount = 0

        if cl.trans_type == "DEBIT":
            coinSummaryLedger.total_coin = coinSummaryLedger.total_coin - coin
        elif cl.trans_type == "CREDIT":
            coinSummaryLedger.total_coin = coinSummaryLedger.total_coin + coin

        coinSummaryLedger.save()
        push_service = FCMNotification(api_key=settings.FCM_SERVER_API_KEY)

        isToNotify = False
        summarySer = CoinSummaryLedgerSerializer(coinSummaryLedger)
        data = summarySer.data
        conConfig = Config.objects.filter(
            key="CoinMaster"
        )
        if conConfig.count() <= 0:
            conConfig = Config()
            conConfig.key = "CoinMaster"
            conConfig.value = "0"
        else:
            conConfig = conConfig[0]
            # conConfig.value = str(0)
            # conConfig.subvalue = str(-1)

        if cl.trans_type == "DEBIT":
            conConfig.value = str(int(conConfig.value) - coin)
        elif cl.trans_type == "CREDIT":
            conConfig.value = str(int(conConfig.value) + coin)
        conConfig.save()

        data_message = {
            "coin": coin,
            "type": type,
            "tran_type": tranType,
            "total_coin": coinSummaryLedger.total_coin,
        }
        registration_id = None
        message_title = None
        message_body = None
        if type == "LOGIN_REFER":
            isToNotify = True
            registration_id = _user.fcm_token
            message_title = "Wow! congratulations"
            message_body = "You have won " + \
                str(coin)+" F-Coin for your new login."
        elif type == "REFERED":
            isToNotify = True
            registration_id = _user.fcm_token
            message_title = "Wow! congratulations"
            message_body = "You have won " + \
                str(coin)+" F-Coin by refering to " + \
                receive_on_behalf.name+"."
        elif type == "COIN_RECEIVE":
            isToNotify = True
            registration_id = _user.fcm_token
            message_title = "Received " + str(coin) + " F-coin"
            message_body = "You have received " + \
                str(coin)+" F-Coin from user " + \
                receive_on_behalf.name+" " + notifyStatement
        result = {}
        if isToNotify:
            result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                       message_body=message_body, data_message=data_message, click_action="FLUTTER_NOTIFICATION_CLICK")
        return result
    except Exception as etc:
        print(etc)

    return 0


def getConfig(vKey):
    conConfig = Config.objects.filter(
        key=vKey
    )
    if conConfig.count() > 0:
        return conConfig[0]
    else:
        return None


class RedeemCoin(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        coin = request.data["coin"]
        upi = request.data["upi"]
        summary = CoinSummaryLedger.objects.get(user=request._user)

        if coin > summary.total_coin:
            return Response({"status": False, "error": 1001, "message": "redeem coin is greater then Coin available"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            summary.total_coin = summary.total_coin - coin
            conConfig = getConfig("CoinMaster")
            conConfig.value = str(int(conConfig.value) - coin)
            coinSingle = getConfig("SingleCoinValue")
            singleCoinValue = int(coinSingle.value)
            redeemProcessingFee = int(getConfig("redeemProcessingFee").value)
            coinInRupee = math.ceil(coin/singleCoinValue)
            finalAmountRedeem = coinInRupee - \
                (coinInRupee * (redeemProcessingFee/100))
            cl = CoinLedger()
            cl.user = request._user
            cl.number_of_coin = coin
            cl.receive_from = request._user
            cl.receive_on_behalf = request._user
            cl.type = "REDEEM"
            cl.trans_type = "DEBIT"
            cl.redeem_upi = upi
            cl.redeem_status = "init"
            cl.remark = str(coin) + " coin to rupee " + str(coinInRupee) + \
                " + PF "+str(redeemProcessingFee)+"="+str(finalAmountRedeem)
            cl.transcation_number = "000"
            cl.save()
            summary.save()
            conConfig.save()
            paymentKey = getConfig("userKey")
            razorPayAccount = getConfig("razorpayxAccount")
            response, status_code = api.razorpayx.payout(
                razorPayAccount, paymentKey, finalAmountRedeem, upi, request._user, cl.id, coin)
            if status_code == 200:
                cl.transcation_number = response["id"]
                cl.redeem_status = response["status"]
                cl.remark = cl.remark + " utr " + str(response["utr"])
                cl.save()
                return Response({"status": True, "error": 0, "message": "Payout successfull", "payload": {
                    "utr": str(response["utr"])
                }}, status=status.HTTP_200_OK)
            else:
                cl.transcation_number = response["error"]["code"]
                cl.redeem_status = "failed"
                cl.remark = cl.remark + " error " + \
                    str(response["error"]["description"])
                cl.save()
                summary.total_coin = summary.total_coin + coin
                conConfig.value = str(int(conConfig.value) + coin)
                summary.save()
                conConfig.save()
                return Response({"status": False, "error": 1002, "message": "Payment gateway error", "payload":  response}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EntertainmentView(APIView):
    def get(self, request):
        entertaimentImage = EventImage.objects.all().order_by('-timestamp')
        image = EventImageSerializer(entertaimentImage, many=True)
        entertaimentVideo = EventVideo.objects.all().order_by('-timestamp')
        video = EventVideoSerializer(entertaimentVideo, many=True)
        data = list(chain(image.data, video.data))

        return Response(data, status=status.HTTP_201_CREATED)


class ChatterBotApiView(APIView):
    """
    Provide an API endpoint to interact with ChatterBot.
    """

    chatterbot = bot

    def post(self, request):
        # user = request.user
        msg = JSONParser().parse(request)
        response = bot.get_response(msg['msg'])
        chatresponse = str(response)
        value = {
            # 'sender': user.userId,
            'message': msg['msg'],
            'reply': chatresponse
        }
        # bot_serializer = ChatBotSerializers(data=value)
        # if bot_serializer.is_valid():
        #     bot_serializer.save()
        return Response({"status": True, "message": chatresponse},
                        status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """
        Return data corresponding to the current conversation.
        """
        user = request.user
        data = ChatBot.objects.filter(
            sender=user.id).order_by('-timestamp').all()
        data_serializers = ChatterBotSerializers(data, many=True)
        return Response({"status": True, "message": data_serializers.data},
                        status=status.HTTP_201_CREATED)
        # return JsonResponse({
        #     'name': "test"
        # })


class LiveStreamView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = LiveStream.objects.filter(
            is_active=True, user=user.id).order_by('-start_date')
        data_serializers = LiveStreamSerializer(data, many=True)
        return Response({"status": True, "data": data_serializers.data}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        live_stream = LiveStream.objects.get(
            id=request.data["id"], user=request.user)
        live_stream.is_active = False
        live_stream.save()
        return Response({"delete": True, "message": "Live Stream Deleted Successfully."}, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.POST._mutable:
            request.POST._mutable = True
        request.data["user"] = request._user.id
        user = request.user

        if request.data.get("id") == None:
            serializer = LiveStreamSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"status": True, "message": "Live Stream Added Successfully."}, status=status.HTTP_201_CREATED)
        else:
            live_stream = LiveStream.objects.get(id=request.data["id"])
            live_stream.event_name = request.data["event_name"]
            live_stream.event_category = request.data["event_category"]
            live_stream.event_description = request.data["event_description"]
            live_stream.start_date = request.data["start_date"]
            live_stream.start_time = request.data["start_time"]
            live_stream.end_time = request.data["end_time"]
            live_stream.user_id = user.id
            live_stream.is_active = request.data["is_active"]
            live_stream.save()
            return Response({"status": True, "message": "Live Stream Updated Successfully."}, status=status.HTTP_201_CREATED)


# class LiveStreamBroadcast(APIView):
#     def get(self, request):
#         return start_video_stream()


class HelpAndFaqsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = HelpAndFaqs.objects.filter(
            is_active=True).order_by('-timestamp')
        data_serializers = HelpAndFaqsSerializer(data, many=True)
        return Response({"status": True, "data": data_serializers.data}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        faqs = HelpAndFaqs.objects.get(id=request.data["id"])
        faqs.is_active = False
        faqs.save()
        return Response({"delete": True, "message": "Help and Faqs Deleted Successfully."}, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.POST._mutable:
            request.POST._mutable = True
        request.data["user"] = request._user.id

        if request.data.get("id") == None:
            vstatus = False
            verror = None
            serializer = HelpAndFaqsSerializer(data=request.data)

            try:
                vstatus = serializer.is_valid(raise_exception=True)
            except Exception as error:
                verror = error

            if vstatus:
                serializer.save()
                return Response({"status": True, "message": "Help and Faqs Added Successfully."}, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"status": vstatus,
                     "error": str(verror)
                     }, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            faqs = HelpAndFaqs.objects.get(id=request.data["id"])
            faqs.title = request.data["title"]
            faqs.description = request.data["description"]
            faqs.is_active = request.data["is_active"]
            faqs.save()
            return Response({"status": True, "message": "Help and Faqs Updated Successfully."}, status=status.HTTP_201_CREATED)


class MarketingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = Marketing.objects.filter(
            is_active=True, is_delivary=True, is_pending=True).order_by('-timestamp')
        data_serializers = MarketingSerializer(data, many=True)
        return Response({"status": True, "data": data_serializers.data}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        marketing = Marketing.objects.get(id=request.data["id"])
        marketing.is_active = False
        marketing.save()
        return Response({"delete": True, "message": "Marketing Deleted Successfully."}, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.POST._mutable:
            request.POST._mutable = True
        request.data["user"] = request._user.id

        if request.data.get("id") == None:
            vstatus = False
            verror = None
            serializer = MarketingSerializer(data=request.data)

            try:
                vstatus = serializer.is_valid(raise_exception=True)
            except Exception as error:
                verror = error

            if vstatus:
                serializer.save()
                return Response({"status": True, "message": "Marketing Added Successfully."}, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"status": vstatus,
                     "error": str(verror)
                     }, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            marketing = Marketing.objects.get(id=request.data["id"])
            marketing.title = request.data["title"]
            marketing.link = request.data["link"]
            if request.data["photo"] is not None:
                marketing.photo = request.data["photo"]
            marketing.time = request.data["time"]
            marketing.date = request.data["date"]
            marketing.description = request.data["description"]
            # marketing.is_active = request.data["is_active"]
            # marketing.is_pending = request.data["is_pending"]
            marketing.save()
            return Response({"status": True, "message": "Marketing Updated Successfully."}, status=status.HTTP_201_CREATED)


class MarketingPendingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = Marketing.objects.filter(
            is_active=True, is_delivary=False, is_pending=False).order_by('-timestamp')
        data_serializers = MarketingSerializer(data, many=True)
        return Response({"status": True, "data": data_serializers.data}, status=status.HTTP_201_CREATED)


def stream(request):
    context = {}
    return render(request, 'stream/main.html', context=context)


class OldCustomerDataView(generics.CreateAPIView):
    serializer_class = OldCustomerDataExcelUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        reader = pd.read_csv(file)
        for _, row in reader.iterrows():
            new_file = User(
                password=row["password"],
                name=row['name'],
                email=row["email"],
                mobile=row["mobile"],
                country_code=row["country_code"],
                role=row["role"],
            )
            new_file.save()
        return Response({"status": True, "message": "Data inserted Successfully."}, status=status.HTTP_201_CREATED)


mycursor = connection.cursor()

# k4q7Ejo4XRWgCFKc4qM7ncL57hLtwsaHZmf1cR3q
@api_view(['POST', ])
@permission_classes([IsAuthenticated])
def pushnotification(request):
    if request.method == 'POST':
        sms = request.POST.get('sms', "")
        notify = request.POST.get('notify', "")
        email = request.POST.get('email', "")
        if sms == str(1):
            sql = 'SELECT mobile FROM users_user AS u JOIN api_notification AS n ON n.user_id = u.id WHERE n.user_id = u.id'
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            print(myresult)
            for x in myresult:
                phone = "+91" + \
                    str(x).replace(',', '').replace(
                        '(', '').replace(')', '').replace('\'', '')
                api.sms.PushSMS(phone)

        if email == str(1):
            sql = 'SELECT email FROM users_user AS u JOIN api_notification AS n ON n.user_id = u.id WHERE n.user_id = u.id'
            mycursor.execute(sql)
            mails = mycursor.fetchall()
            for m in mails:
                mail = str(m).replace(',', '').replace(
                    '(', '').replace(')', '').replace('\'', '')
                user_email = mail
                email_message = "This is the TEST mail from Festum Evento!!"
                htmlgen = '<p> It seems you have new notification </p>' + email_message
                send_mail('New Updates', email_message, 'raj.scalelot@gmail.com', [
                    user_email], fail_silently=False, html_message=htmlgen)

        if notify == str(1):
            data = request.data
            sql = 'SELECT apptoken FROM userapi_fcmtoken where user_id in (' + \
                data['users'] + ');'
            mycursor.execute(sql)
            tokens = mycursor.fetchall()
            for t in tokens:
                tokenin = str(t).replace(',', '').replace(
                    '(', '').replace(')', '').replace('\'', '')
                tokens = [tokenin]
                fcm.sendPush("Evento Package", "test notification", tokens)

        return JsonResponse({
            'message': "Successfully Sended",
            'data': 1,
            'isSuccess': True
        })
    return JsonResponse({
        'message': "Connection error",
        'data': '0',
        'isSuccess': False
    }, status=400)


class OrganizerEventVideoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.POST._mutable:
            request.POST._mutable = True
        request.data["user"] = request._user.id
        if request.data.get("id") == None:
            vstatus = False
            verror = None
            serializer = OrganizerEventVideoSerializer(data=request.data)

            try:
                vstatus = serializer.is_valid(raise_exception=True)
            except Exception as error:
                verror = error

            if vstatus:
                serializer.save()
                return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"status": vstatus,
                     "error": str(verror)
                     }, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            eventvideo = OrganizerEventVideo.objects.get(id=request.data["id"])
            eventvideo.video = request.data["video"]
            eventvideo.thumbnail = request.data["thumbnail"]
            eventvideo.is_active = request.data["is_active"]
            eventvideo.save()
            return Response({"status": True, "message": "Updated Successfully."}, status=status.HTTP_201_CREATED)

    def get(self, request):

        images = OrganizerEventVideo.objects.filter(
            is_active=True).order_by('timestamp')

        serializer = OrganizerEventVideoSerializer(images, many=True)

        return Response(
            {
                "detail": serializer.data,
            },
            status=status.HTTP_201_CREATED
        )

    def delete(self, request):
        eventvideo = OrganizerEventVideo.objects.get(id=request.data["id"])
        eventvideo.is_active = False
        eventvideo.save()
        return Response({"delete": True, "message": "Deleted Successfully."}, status=status.HTTP_200_OK)


class OrganizerUserViseEventVideoView(APIView):
    def get(self, request):

        images = OrganizerEventVideo.objects.filter(
            is_active=True, user=request._user.id).order_by('timestamp')

        serializer = OrganizerEventVideoSerializer(images, many=True)

        return Response(
            {
                "detail": serializer.data,
            },
            status=status.HTTP_201_CREATED
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def convert(request, price=0):
    if request.method == 'GET':
        c = CurrencyConverter(fallback_on_wrong_date=True)
        usd = c.convert(price, 'INR', 'USD', date=date.today())
        thb = c.convert(price, 'INR', 'THB', date=date.today())
        cny = c.convert(price, 'INR', 'CNY', date=date.today())
        eur = c.convert(price, 'INR', 'EUR', date=date.today())
        rub = c.convert(price, 'INR', 'RUB', date=date.today())
        pkr = c.convert(price, 'INR', 'USD', date=date.today())
        dza = c.convert(price, 'INR', 'USD', date=date.today())
        chn = c.convert(price, 'INR', 'USD', date=date.today())
        jpn = c.convert(price, 'INR', 'USD', date=date.today())
        ken = c.convert(price, 'INR', 'USD', date=date.today())
        tur = c.convert(price, 'INR', 'USD', date=date.today())
        return JsonResponse({
            'message': "Converted successfully",
            'data': {"usd": usd, "thb": thb, "cny": cny, "eur": eur, "rub": rub, "pkr": pkr, "dza": dza, "chn": chn, "jpn": jpn, "ken": ken, "tur": tur},
            'isSuccess': True
        }, status=status.HTTP_200_OK)
    return JsonResponse({
        'message': "Connection error",
        'data': '0',
        'isSuccess': False
    }, status=status.HTTP_400_BAD_REQUEST)


class CommentsAndRatingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            avg_rating = 0
            avg_user_rating = 0
            avg_rating_count = 0
            avg_user_rating_count = 0
            is_repeated = False
            eventRegistration = None
            offer = None
            if(request.data.get("is_event") != None and request.data["is_event"] == True):
                print('is_event')
                eventRegistration = EventRegistration.objects.get(
                    id=request.data["occasion"]
                )
                print('eventRegistration 1', eventRegistration)
                all_car = CommentsAndRating.objects.filter(
                    occasion__event_id=eventRegistration.event.id,
                    user=request._user,
                    is_active=True
                )
                if(all_car.count() > 0):
                    is_repeated = True
                else:
                    max_car = CommentsAndRating.objects.filter(
                        occasion=eventRegistration,
                        is_active=True
                    ).order_by('-id')
                    if(max_car.count() > 0):
                        avg_rating_count = 1
                        avg_user_rating_count = 1
                        avg_rating = max_car[0].avg_rating
                        avg_user_rating = max_car[0].avg_user_rating

            if(request.data.get("is_offer") != None and request.data["is_offer"] == True):
                print('is_offer')
                offer = LocalOffer.objects.get(
                    id=request.data["offer"]
                )
                all_car = CommentsAndRating.objects.filter(
                    offer=offer,
                    user=request._user,
                    is_active=True
                )
                if(all_car.count() > 0):
                    is_repeated = True
                else:
                    max_car = CommentsAndRating.objects.filter(
                        offer__shop_id=offer.shop.id,
                        is_active=True
                    ).order_by('-id')
                    if(max_car.count() > 0):
                        avg_rating_count = 1
                        avg_user_rating_count = 1
                        avg_rating = max_car[0].avg_rating
                        avg_user_rating = max_car[0].avg_user_rating

            if is_repeated == False:
                avg_rating = (
                    avg_rating + int(request.data.get("rating"))) / (avg_rating_count+1)
                avg_user_rating = (
                    avg_user_rating + int(request.data.get("user_rating"))) / (avg_user_rating_count+1)

                print('eventRegistration', eventRegistration)

                car = CommentsAndRating()
                car.user = request._user
                car.rating = request.data["rating"]
                car.avg_rating = avg_rating
                car.avg_user_rating = avg_user_rating
                car.user_rating = request.data["user_rating"]
                car.title = request.data["title"]
                car.review = request.data["review"]
                car.occasion = eventRegistration
                car.offer = offer
                car.save()
                return Response({"status": True}, status=status.HTTP_200_OK)
            else:
                return Response({"status": False, "error": 1001, "detail": "User already is rated and commented"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as err:
            return Response({"status": False, "detail": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        type = request.GET.get('type', '')
        event = None
        offer = None
        all_car = None
        if type == "event":
            event = Event.objects.get(
                id=int(request.GET.get('event', '0'))
            )
            print('event', event)
            all_car = CommentsAndRating.objects.filter(
                occasion__event_id=event.id,
                is_active=True
            ).order_by("-timestamp")
            print('all_car', all_car)
        elif type == "offer":
            offer = LocalOffer.objects.get(
                id=request.GET.get('offer', '')
            )
            all_car = CommentsAndRating.objects.filter(
                offer=offer,
                is_active=True
            ).order_by("-timestamp")

        ser_all_car = CommentsAndRatingSerializer(all_car, many=True)
        return Response({"status": True, "detail": ser_all_car.data}, status=status.HTTP_200_OK)


class AskCommentsAndRatingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        type = request.GET.get('type', '@')
        id = request.GET.get('id', '@')

        if type == "@" and id == "@":
            event_reg_ids = CommentsAndRating.objects.filter(
                user=request._user,
            ).values_list('occasion', flat=True)

            offer_ids = CommentsAndRating.objects.filter(
                user=request._user,
            ).values_list('offer', flat=True)

            attendee = Attendee.objects.filter(
                user=request._user,
                is_avail=True,
                event_reg__start_date__lte=datetime.now().date(),
            ).exclude(event_reg_id__in=event_reg_ids)

            attendee = AttendeeSmallSerializer(attendee, many=True)
            attendee = attendee.data
            attendee_data = []
            for att in attendee:
                attendee_data.append(att["event_reg"])

            bookings = LocalOfferBooking.objects.filter(
                user=request._user,
                is_avail=True,
                local__start_date__lte=datetime.now().date(),
            ).exclude(local_id__in=offer_ids)

            bookings = LocalOfferBookingSerializerSmall(bookings, many=True)
            bookings = bookings.data
            bookings_data = []
            for book in bookings:
                bookings_data.append(book["local"])
            return Response({"status": True, "events": attendee_data, 'offers': bookings_data}, status=status.HTTP_200_OK)
        else:
            count = 0
            if type == "occasion":
                comments = CommentsAndRating.objects.filter(
                    user=request._user,
                    occasion__id=id
                )
                count = comments.count()
            elif type == 'offer':
                comments = CommentsAndRating.objects.filter(
                    user=request._user,
                    offer__id=id
                )
                count = comments.count()
            return Response({"status": True, "isComment": count > 0}, status=status.HTTP_200_OK)


class OurProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.POST._mutable:
            request.POST._mutable = True
        # request.data["user"] = request._user.id
        if request.data.get("id") == None:
            vstatus = False
            verror = None
            serializer = OurProductSerializer(data=request.data)

            try:
                vstatus = serializer.is_valid(raise_exception=True)
            except Exception as error:
                verror = error

            if vstatus:
                serializer.save()
                return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"status": vstatus,
                     "error": str(verror)
                     }, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            product = OurProduct.objects.get(id=request.data["id"])
            product.name = request.data["name"]
            product.link = request.data["link"]
            if request.data["icon"] is not None:
                product.icon = request.data["icon"]
            product.description = request.data["description"]
            product.is_active = request.data["is_active"]
            product.save()
            return Response({"status": True, "message": "Updated Successfully."}, status=status.HTTP_201_CREATED)

    def get(self, request):

        product = OurProduct.objects.filter(
            is_active=True).order_by('timestampe')

        serializer = OurProductSerializer(product, many=True)

        return Response(
            {
                "detail": serializer.data,
            },
            status=status.HTTP_201_CREATED
        )

    def delete(self, request):
        product = OurProduct.objects.get(id=request.data["id"])
        product.is_active = False
        product.save()
        return Response({"delete": True, "message": "Deleted Successfully."}, status=status.HTTP_200_OK)


class TopicView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.POST._mutable:
            request.POST._mutable = True
        # request.data["user"] = request._user.id
        if request.data.get("id") == None:
            vstatus = False
            verror = None
            serializer = TopicSerializer(data=request.data)
            print('data', serializer)

            try:
                vstatus = serializer.is_valid(raise_exception=True)
            except Exception as error:
                verror = error

            if vstatus:
                serializer.save()
                return Response({"status": True, "detail": serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"status": vstatus,
                     "error": str(verror)
                     }, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            product = Topic.objects.get(id=request.data["id"])

            product.product_id = request.data["product_id"]
            product.link = request.data["link"]
            if request.data["icon"] is not None:
                product.icon = request.data["icon"]
            product.is_active = request.data["is_active"]
            product.save()
            return Response({"status": True, "message": "Updated Successfully."}, status=status.HTTP_201_CREATED)

    def get(self, request):

        product = Topic.objects.filter(
            is_active=True).order_by('timestampe')

        serializer = TopicSerializer(product, many=True)

        return Response(
            {
                "detail": serializer.data,
            },
            status=status.HTTP_201_CREATED
        )

    def delete(self, request):
        product = Topic.objects.get(id=request.data["id"])
        print(product)
        product.is_active = False
        product.save()
        return Response({"delete": True, "message": "Deleted Successfully."}, status=status.HTTP_200_OK)
