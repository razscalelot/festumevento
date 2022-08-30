from django.conf.urls import url
from django.urls import path,include
from . import views

urlpatterns = [
    path("register",views.regeister, name="register"),
    path('', include("django.contrib.auth.urls") ),
    path('home',views.index, name="Home"),
    path('paid',views.updatePaid, name="Paid")
]
