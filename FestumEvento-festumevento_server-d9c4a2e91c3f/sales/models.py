from django.db import models
from users.models import User

# Create your models here.
class SalesAgentDetail(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    mobile = models.CharField(max_length=10, unique=True)
    active = models.BooleanField(default=True)
    verify = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)


class SalesLead(models.Model):
    leadUser = models.ForeignKey(User, on_delete=models.CASCADE,related_name='%(class)s_Lead_user')
    orgUser = models.ForeignKey(User, on_delete=models.CASCADE,related_name='%(class)s_Org_user')
    amount = models.DecimalField(decimal_places=2, max_digits=7)
    isPayed = models.BooleanField(default=False)
    createdon = models.DateTimeField(auto_now_add=True)
