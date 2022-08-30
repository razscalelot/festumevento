from django.forms import ModelForm,Form
from django import forms
from .models import SalesAgentDetail
from users.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from django.db import models
from django.core.exceptions import ValidationError
from .models import SalesLead

class SalesAgentForm(ModelForm):
    class Meta:
        model = SalesAgentDetail
        fields = ['name','email','mobile']

class RegeisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegeisterForm, self).__init__(*args, **kwargs)
        self.fields['role'].disabled = True

    class Meta:
        model = User
        fields = ['name','email','mobile','role']


class LeadForm(Form):
    Organiser_mobile =forms.IntegerField(label='Organiser Mobile Number')
    def clean(self):
        cleanData = self.cleaned_data
        a = cleanData.get("Organiser_mobile")
        try:
            orgUser = User.objects.get(mobile = cleanData.get("Organiser_mobile"))
        except Exception as error:
            raise ValidationError("No Organiser Found")
        if orgUser.role == "Organiser":
            sales = SalesLead.objects.filter(orgUser = orgUser)
            if sales.count() <= 0:
                return cleanData
            else:
                raise ValidationError("Organiser already Register")
        else:
            raise ValidationError("User is not Organiser")