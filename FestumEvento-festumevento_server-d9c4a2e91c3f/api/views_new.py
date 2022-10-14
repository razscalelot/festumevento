from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializars import *
from .models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models import F,Q
from django.db.models import Prefetch
from datetime import datetime,date
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


class FrequentlyAskedQuestionsView(APIView):

    def post(self, request):
        faq_ser = FrequentlyAskedQuestionsSerializer(data=request.data)
        faq_ser.is_valid(raise_exception=True)
        faq_ser.save()
        return Response({"status": True, "detail": serializers.data}, status=status.HTTP_201_CREATED)


    def get(self, request):
        today = datetime.today()
        today = date(today.year,today.month,today.day)
        faq = FrequentlyAskedQuestions.objects.filter(
            Q(start_date__isnull=True) | Q(start_date__gte = today),
            Q(end_date__isnull=True) | Q(end_date__lte = today),
            is_active = True,            
        ).order_by("sequence")

        faq_seq = FrequentlyAskedQuestionsSerializer(faq, many=True)

        return Response(
                { 
                    "status": True,
                    "detial": faq_seq.data
                },
                status=status.HTTP_200_OK
            )

class WishlistOfferView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        id = request.GET.get('id', 0)
        offer = LocalOffer.objects.get(id=id)
        flag = True
        wishlistdata = WishlistOffer.objects.filter(
            user = request._user,
            offer = offer
        )
        if wishlistdata.count() <= 0:
            wishlist = WishlistOffer()
            wishlist.offer = offer
            wishlist.user = request._user
            wishlist.is_active = True
            flag = True
            wishlist.save()
        else:
            for wish in wishlistdata:
                wish.is_active = not wish.is_active
                wish.timestampe = datetime.today()
                flag = wish.is_active
                wish.save()
                
        return Response({"status": True, "detail":flag}, status=status.HTTP_200_OK)

class WishlistOccationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        id = request.GET.get('id', 0)
        flag = True
        occasion = EventRegistration.objects.get(id=id)
        wishlistdata = WishlistOccation.objects.filter(
            user = request._user,
            occasion = occasion
        )
        wishlist = WishlistOccation()
        if wishlistdata.count() <= 0:
            wishlist.occasion = occasion
            wishlist.user = request._user
            wishlist.is_active = True
            flag = True
            wishlist.save()
        else:
            for wish in wishlistdata:
                wish.is_active = not wish.is_active
                wish.timestampe = datetime.today()
                flag = wish.is_active
                wish.save()
        return Response({"status": True, "detail": flag}, status=status.HTTP_200_OK)

class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        offers = WishlistOffer.objects.filter(
            user = request._user,
            is_active = True
        )
        occasions = WishlistOccation.objects.filter(
            user = request._user,
            is_active = True
        )

        offers_ser = WishlistOfferSerializer(offers, many=True)
        occasion_ser = WishlistOccationSerializer(occasions, many=True)

        occasions_data = occasion_ser.data
        offers_data = offers_ser.data
        for occa in occasions_data:
            i = occa['occasion']
            price = PriceMatrix.objects.filter(
                    event_reg = i["id"]
                ).order_by('number')
            priceserializer = PriceMatrixSerializer(price, many=True)
            i["price_matric"] = priceserializer.data
            try:
                wishlist = WishlistOccation.objects.filter(
                    occasion = i["id"],
                    user = request._user
                )
                if wishlist.count() > 0:
                    i["is_wishlist"] = wishlist[0].is_active
                else:
                    i["is_wishlist"] = False
            except:
                i["is_wishlist"] = False

        for offer in offers_data:
            i = offer['offer']
            category = ShopCategory.objects.filter(
                    id = i["shop"]["category"]
                )
            if(category.count() > 0):
                i["shop"]["category"] = ShopCategorySerializer(category[0]).data
            products = Offer_Product.objects.filter(
                local_offer = i["id"]
            ).order_by('id')
            try:
                wishlist = WishlistOffer.objects.filter(
                    offer = i["id"],
                    user = request._user
                )
                if wishlist.count() > 0:
                    i["is_wishlist"] = wishlist[0].is_active
                else:
                    i["is_wishlist"] = False
            except:
                i["is_wishlist"] = False
            if products.count() >=1:
                lastProduct = products[products.count() -1]
                offers = Offer_Discount.objects.filter(
                    product = lastProduct.id
                )
                if offers.count() >=1:
                    lastOffer = offers[offers.count()-1]
                    discount = ""
                    price = str(int(float(lastOffer.price)))
                    if lastOffer.discount_type == "PERCENTAGE":
                        discount = "Upto "+price + "% off"
                    elif lastOffer.discount_type == "AMOUNT":
                        discount = "Upto ₹"+price + " off"
                    i["offer"] = discount

        return Response(
            {"status": True,
             "offers": offers_data,
             "occasions": occasions_data
             }, 
            status=status.HTTP_200_OK)

class SeatingArrangementMasterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        seats = SeatingArrangementMaster.objects.filter(
            is_active = True
        );
        seats_seq = SeatingArrangementMasterSerializer(seats, many=True)

        return Response(
            {
                "status": True,
                "data": seats_seq.data
             }, 
            status=status.HTTP_200_OK)


class SeatingArrangementBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):        
        data = request.data
        # seat = SeatingArrangementMaster.objects.get(
        #     id = data['seat']
        # )
        # data['seat'] = seat
        ser = SeatingArrangementBookingSerializerInsert(data=data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({"status": True, "detail": ser.data}, status=status.HTTP_201_CREATED)

    def get(self, request):
        occasion = int(str( request.GET.get('occasion', 0)))

        seats= SeatingArrangementBooking.objects.filter(occasion_id=occasion)

        seats_ser = SeatingArrangementBookingSerializer(seats, many=True)
        return Response({"status": True, "detail": seats_ser.data}, status=status.HTTP_200_OK)


    def put(self, request):
        occasion = int(str( request.GET.get('occasion', 0)))
        id = request.data['id']

        seats = SeatingArrangementBooking.objects.filter(id=id, occasion_id=occasion)
        serializer = SeatingArrangementBookingSerializerInsert(seats, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"status": True, "detail": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": False, "error": serializer.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)
