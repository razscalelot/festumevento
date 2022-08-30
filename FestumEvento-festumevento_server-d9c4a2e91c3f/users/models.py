from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser
from django.db import models
from django.core.validators import validate_email


# Create your models here
class UserManager(BaseUserManager):
    def create_user(self, name, email, mobile, country_code, role, password=None, confirm_password=None, refer_code=None, my_refer_code=None, fcm_token=None, about=None):
        if not email:
            return ValueError("We need your email address")
        try:
            validate_email(email)
        except:
            return ValueError("Invalid Email address")

        if not password:
            return ValueError("You must have strong password")
        
        if len(password) < 8:
            return ValueError("You must have strong password")
        else:
            if password != confirm_password:
                return ValueError("Confirm passwords do not match.")

        if not name:
            return ValueError("Please let me know your name")

        if not mobile:
            return ValueError("We need your mobile number")

        if not country_code:
            return ValueError("*country code")
        if not role:
            return ValueError("*Role")

        userObj = self.model(
            email=self.normalize_email(email),
            name=name,
            mobile=mobile,
            about=about,
            country_code=country_code,
            role=role,
            refer_code= refer_code,
            my_refer_code= my_refer_code,
            fcm_token= fcm_token
        )
        userObj.set_password(password)
        userObj.save(using=self._db)
        return userObj

    def create_staffuser(self, name, email, about, mobile, country_code, role, password=None):
        if not email:
            return ValueError("We need your email address")
        try:
            validate_email(email)
        except:
            return ValueError("Invalid Email address")

        userObj = self.model(
            email=self.normalize_email(email),
            name=name,
            mobile=mobile,
            about=about,
            country_code=country_code,
            role=role
        )
        userObj.set_password(password)
        userObj.save(using=self._db)
        return userObj

    def create_superuser(self, name, mobile, password=None):
        if not mobile:
            return ValueError("We need your email address")
        # try:
        #     validate_email(email)
        # except:
        #     return ValueError("Invalid Email address")

        userObj = self.model(
            mobile=mobile,
            name=name,
            admin=True,
            verify=True
        )
        userObj.set_password(password)
        userObj.save(using=self._db)
        return userObj


class User(AbstractBaseUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    mobile = models.CharField(max_length=10, unique=True)
    country_code = models.CharField(max_length=6)
    role = models.CharField(max_length=50, unique=False)
    about = models.TextField(null=True, blank=True)
    admin = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    verify = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    refer_code = models.CharField(max_length=50, blank=True, null=True)
    my_refer_code = models.CharField(max_length=50, blank=True, null=True, unique=True)
    fcm_token = models.CharField(max_length=255, blank=True, null=True, unique=False)

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.mobile+" - "+self.name

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active

    @property
    def is_staff(self):
        return True

    objects = UserManager()


class OtpLog(models.Model):
    mobile = models.CharField(max_length=10)
    otp = models.CharField(max_length=10, null=True, blank=True)
    smsKey = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
