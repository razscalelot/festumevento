# Create your views here.
from django.shortcuts import redirect, render
from .form import SalesAgentForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .form import RegeisterForm, LeadForm
from users.models import User
from api.models import Config
from .models import SalesLead
from django.core.exceptions import ValidationError

# Create your views here.


def regeister(response):
    if response.method == "POST":
        response.POST = response.POST.copy()
        response.POST["role"] = "Sales"
        form = RegeisterForm(response.POST, initial={'role': 'Sales'})
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
    else:
        form = RegeisterForm(initial={'role': 'Sales'})
    return render(response, "register.html", {"form": form})


def index(response):
    if response.method == "POST":
        form = LeadForm(response.POST)
        if form.is_valid():
            a = response.POST.get("Organiser_mobile")
            try:
                orgUser = User.objects.get(mobile=a)
                config = Config.objects.get(
                    key="SalesAmount"
                )
                sale = SalesLead()
                sale.leadUser = response.user
                sale.orgUser = orgUser
                sale.amount = config.value
                sale.save()
            except Exception as error:
                raise ValidationError("No Organiser Found")
    else:
        form = LeadForm()
    totalAmountpaid = 0
    totalAmountNotPaid = 0
    userData = []
    if response.user.is_authenticated:
        data = SalesLead.objects.filter(
            leadUser=response.user).order_by("-createdon")
        for a in data:
            if a.isPayed:
                totalAmountpaid = totalAmountpaid + a.amount
            else:
                totalAmountNotPaid = totalAmountNotPaid + a.amount
        if response.user.is_admin:
            userData = User.objects.filter(role="Sales")
            for user in userData:
                totalAmountpaid = 0
                totalAmountNotPaid = 0
                data = SalesLead.objects.filter(
                    leadUser=user).order_by("-createdon")
                for a in data:
                    if a.isPayed:
                        totalAmountpaid = totalAmountpaid + a.amount
                    else:
                        totalAmountNotPaid = totalAmountNotPaid + a.amount
                setattr(user, "totalAmountPaid", totalAmountpaid)
                setattr(user, "totalAmountNotPaid", totalAmountNotPaid)
                #user["totalAmountPaid"]  = 30
                #user["totalAmountNotPaid"]  = 30
    else:
        data = []
    my_param = response.GET.get('mobile')
    if my_param != None:
        orgUser = User.objects.get(mobile=my_param)
        data = SalesLead.objects.filter(
            leadUser=orgUser).order_by("-createdon")
        for a in data:
            if a.isPayed:
                totalAmountpaid = totalAmountpaid + a.amount
            else:
                totalAmountNotPaid = totalAmountNotPaid + a.amount

    return render(response, "home.html", {
        "leadform": form,
        'lead': data,

        'totalAmountpaid': totalAmountpaid,
        'totalAmountNotPaid': totalAmountNotPaid,
        'userData': userData, 'selectedUser': my_param})


def updatePaid(response):
    if response.method == "POST":
        a = 0
        salesUser = User.objects.get(mobile=response.POST["selectedUser"])
        data = SalesLead.objects.filter(
            leadUser=salesUser).order_by("-createdon")
        selectedID = response.POST.getlist('selected_options')
        for lead in data:
            isLead = True
            for _id in selectedID:
                if lead.id == int(_id):
                    lead.isPayed = True
                    lead.save()
                    isLead = False
            if isLead:
                lead.isPayed = False
                lead.save()

        print(response.POST)

    response = redirect('/salespanel/home?mobile=' +
                        response.POST["selectedUser"])
    return response
