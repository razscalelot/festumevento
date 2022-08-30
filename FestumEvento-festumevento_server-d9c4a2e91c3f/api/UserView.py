from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializars import *
from .models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models import F
from django.db.models import Prefetch
from django.db.models.functions import Radians, Power, Sin, Cos, ATan2, Sqrt, Radians
# Create your views here.

class EventView(APIView):

    def get(self, request):
        try:
            current_lat = request.GET.get('lat', 0)
            current_long = request.GET.get('long', 0)
            dlat = Radians(F('latitude') - current_lat)
            dlong = Radians(F('longitude') - current_long)

            a = (Power(Sin(dlat/2), 2) + Cos(Radians(current_lat)) 
                * Cos(Radians(F('latitude'))) * Power(Sin(dlong/2), 2)
            )

            c = 2 * ATan2(Sqrt(a), Sqrt(1-a))
            d = 6371 * c
            events = EventRegistration.objects.annotate(distance=d).order_by('distance').filter(distance__lt=10)

            serializer = EventRegistrationSerializer(events, many=True)
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