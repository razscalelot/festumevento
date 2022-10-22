from django.db import models
from sqlalchemy import null
from users.models import User
from enum import Enum
from django.core.validators import MaxValueValidator
from datetime import datetime
from io import BytesIO
from PIL import Image
from django.core.files import File
from django.core.exceptions import ValidationError
import xml.etree.cElementTree as et

# Create your models here.


def nullStr(statements):
    if statements != None:
        statements = str(statements)

    if statements and not statements.isspace():
        return str(statements)
    else:
        return ""


def compress(image):
    im = Image.open(image)
    # create a BytesIO object
    im = im.convert('RGB')
    im_io = BytesIO()
    # save image to BytesIO object
    im.save(im_io, 'JPEG', quality=50)
    # create a django-friendly Files object
    new_image = File(im_io, name=image.name)
    return new_image


class Event(models.Model):
    name = models.CharField(max_length=255)
    event_type = models.CharField(max_length=50)
    event_category = models.CharField(max_length=100, blank=False, null=False)
    is_other = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# class AboutEvent(models.Model):
#     event = models.ForeignKey(
#         Event, related_name='about', on_delete=models.CASCADE)
#     start_to_end_date = models.CharField(max_length=255)
#     start_time = models.CharField(max_length=100)
#     end_time = models.CharField(max_length=100)
#     about_event = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.event.name


class SubscriptionMaster(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=7)
    no_of_post = models.IntegerField()
    max_days = models.IntegerField()
    name = models.CharField(max_length=255)
    validity_days = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return nullStr(self.name)


class PaymentTransaction(models.Model):
    our_payment_id = models.CharField(max_length=200, unique=True)
    amount = models.DecimalField(decimal_places=2, max_digits=7)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)

    def __str__(self):
        return nullStr(self.amount) + " - " + nullStr(self.timestamp)


class SubscriptionTransaction(models.Model):
    subscription = models.ForeignKey(
        SubscriptionMaster, on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2, max_digits=7)
    no_of_post = models.IntegerField()
    used_post = models.IntegerField()
    max_days = models.IntegerField()
    used_days = models.IntegerField()
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_status = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    payment = models.ForeignKey(PaymentTransaction, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()

    def __str__(self):
        return nullStr(self.subscription) + " - " + nullStr(self.price)




DISCOUNT_TYPE = {('discount_on_total_bill', 'Discount On Total Bill'),
                 ('discount_on_equipment_or_item', 'Discount On Equipment Or Item'),
                 ('advance_and_discount_confirmation', 'Advance And Discount Confirmation')
                 }


class Discounts(models.Model):
    discountsId = models.AutoField(primary_key=True)
    discount_type = models.CharField(max_length=50, choices=DISCOUNT_TYPE)
    discount = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.discount



class OrgDiscounts(models.Model):
    event_id = models.ForeignKey(Event, related_name='event_id',  on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    discount_type = models.CharField(max_length=50, choices=DISCOUNT_TYPE)
    discount = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.discount)


class OrgEquipmentId(models.Model):
    orgdiscount_id = models.ForeignKey(OrgDiscounts, related_name="orgdiscount_id", on_delete=models.CASCADE)
    equipment_id = models.ForeignKey('SeatingArrangementBooking', related_name='equipment_id', on_delete=models.CASCADE)    
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.equipment_id)




class StatusChoice(Enum):
    save = "SAVE"
    submit = "SUBMIT"
    unpaid = "UNPAID"

    @classmethod
    def all(cls):
        return [StatusChoice.save, StatusChoice.submit, StatusChoice.unpaid]


class DiscountChoice(Enum):
    percentage = "PERCENTAGE"
    amount = "AMOUNT"

    @classmethod
    def all(cls):
        return [DiscountChoice.percentage, DiscountChoice.amount]


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    flat_no = models.CharField(max_length=100, null=True, blank=True)
    street_name = models.CharField(max_length=255, null=True, blank=True)
    area_name = models.CharField(max_length=255, null=True, blank=True)
    location_address = models.CharField(max_length=500, null=True, blank=True)
    address = models.CharField(max_length=2000)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pincode = models.PositiveIntegerField(
        validators=[MaxValueValidator(999999)])
    longitude = models.DecimalField(
        max_digits=22, decimal_places=16, null=True)
    latitude = models.DecimalField(max_digits=22, decimal_places=16, null=True)

    permission_letter = models.FileField(
        upload_to='media/file/permission_letter', null=True, blank=True)
    accept_booking = models.BooleanField(default=False)

    location_type = models.CharField(max_length=100)
    occupancy_type = models.CharField(max_length=50)

    capacity = models.IntegerField()

    poster = models.FileField(upload_to='media/image/poster', null=True, blank=True)
    status = models.CharField(max_length=100, choices=[(
        tag.value, tag) for tag in StatusChoice.all()])
    is_verify = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    description = models.CharField(max_length=1000)
    sold = models.IntegerField(default=0)
    is_food = models.BooleanField(default=False)
    food_type = models.CharField(max_length=100, null=True)
    food_description = models.CharField(max_length=500, null=True)
    is_equipment = models.BooleanField(default=False)
    equipment_description = models.CharField(max_length=500, null=True)
    #subscription = models.ForeignKey(SubscriptionTransaction, on_delete=models.CASCADE)

    t_and_c = models.TextField(max_length=5000)
    facebook = models.CharField(max_length=255, blank=True, null=True)
    twitter = models.CharField(max_length=255, blank=True, null=True)
    youtube = models.CharField(max_length=255, blank=True, null=True)
    pinterest = models.CharField(max_length=255, blank=True, null=True)
    instagram = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.CharField(max_length=255, blank=True, null=True)
    orgdiscountsId = models.ForeignKey(OrgDiscounts, on_delete=models.CASCADE, null=True, blank=True)
    calender = models.CharField(max_length=255)
    live = models.BooleanField(default=False)

    # def save(self, *args, **kwargs):
    #     # call the compress function
    #     new_image = compress(self.poster)
    #     # set self.image to new_image
    #     self.poster = new_image
    #     # save
    #     super().save(*args, **kwargs)

    def __str__(self):
        return nullStr(self.event)


class PriceMatrix(models.Model):
    number = models.IntegerField()
    price = models.DecimalField(decimal_places=2, max_digits=7)
    event_reg = models.ForeignKey(EventRegistration, on_delete=models.CASCADE)

    def __str__(self):
        return nullStr(self.event_reg) + " = " + nullStr(self.number) + " = " + nullStr(self.price)


class EventImage(models.Model):
    image = models.ImageField(upload_to='media/image/events')
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    event_reg = models.ForeignKey(EventRegistration, on_delete=models.CASCADE)

    # def save(self, *args, **kwargs):
    #     # call the compress function
    #     new_image = compress(self.image)
    #     # set self.image to new_image
    #     self.image = new_image
    #     # save
    #     super().save(*args, **kwargs)

    def __str__(self):
        return nullStr(self.image.name)


class EventVideo(models.Model):
    video = models.FileField(upload_to='media/video/events')
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='media/video/thumbnail/events', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    event_reg = models.ForeignKey(EventRegistration, on_delete=models.CASCADE)

    # def save(self, *args, **kwargs):
    #     # call the compress function
    #     #new_image = compress(self.image)
    #     # set self.image to new_image

    #     #self.image = new_image
    #     # save
    #     super().save(*args, **kwargs)

    def __str__(self):
        return nullStr(self.video.name)


class EventCompanyDetails(models.Model):
    event_reg = models.ForeignKey(EventRegistration, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    gst = models.FileField(
        max_length=255, upload_to='image/events/company/gst', blank=True, null=True)
    contact_no = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    about = models.TextField()
    flat_no = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pincode = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class EventCompanyImage(models.Model):
    company_id = models.ForeignKey(
        EventCompanyDetails, related_name='image', on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='image/events/company', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return nullStr(self.image.name)


class EventCompanyVideo(models.Model):
    company_id = models.ForeignKey(
        EventCompanyDetails, related_name='video', on_delete=models.CASCADE)
    video = models.FileField(
        upload_to='image/events/company/video', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return nullStr(self.video.name)


class EventPersonalDetails(models.Model):
    event_reg = models.ForeignKey(EventRegistration, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=20)
    is_mobile_hidden = models.BooleanField(default=False)
    alt_mobile_no = models.CharField(max_length=20, blank=True, null=True)
    is_alt_mobile_hidden = models.BooleanField(default=False)
    email = models.CharField(max_length=100)
    is_email_hidden = models.BooleanField(default=True)
    flat_no = models.CharField(max_length=100, blank=True, null=True)
    street = models.CharField(max_length=100, blank=True, null=True)
    area = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class ProductTypeChoice(Enum):
    All = "ALL"
    Specific = "SPECIFIC"

    @classmethod
    def all(cls):
        return [ProductTypeChoice.All, ProductTypeChoice.Specific]


class CapacityTypeChoice(Enum):
    Unlimited = "UNLIMITED"
    Specific = "SPECIFIC"

    @classmethod
    def all(cls):
        return [CapacityTypeChoice.Unlimited, CapacityTypeChoice.Specific]


class ShopCategory(models.Model):
    category_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.category_name


class Shop(models.Model):
    shop_name = models.CharField(max_length=256)
    category = models.ForeignKey(ShopCategory, on_delete=models.CASCADE)
    shop_start_time = models.TimeField()
    shop_end_time = models.TimeField()
    week_days = models.CharField(max_length=7)
    longitude = models.DecimalField(
        max_digits=22, decimal_places=16, null=True)
    latitude = models.DecimalField(max_digits=22, decimal_places=16, null=True)
    address = models.CharField(max_length=2000)
    city = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=255, null=True)
    pincode = models.PositiveIntegerField(
        validators=[MaxValueValidator(999999)], null=True)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return nullStr(self.shop_name)


class LocalOffer(models.Model):
    quantity = models.IntegerField()
    poster = models.ImageField(
        upload_to='media/image/local_offer/poster', max_length=1000)
    offer_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    no_of_days = models.IntegerField()
    is_verify = models.BooleanField(default=False)
    accept_booking = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=100, choices=[(
        tag.value, tag) for tag in StatusChoice.all()])
    subscription = models.ForeignKey(
        SubscriptionTransaction, on_delete=models.CASCADE)
    sold = models.IntegerField(default=0)
    offer_on_product_type = models.CharField(
        max_length=100, choices=[(tag.value, tag) for tag in ProductTypeChoice.all()])

    def save(self, *args, **kwargs):
        # call the compress function
        new_image = compress(self.poster)
        # set self.image to new_image
        self.poster = new_image
        # save
        super().save(*args, **kwargs)

    def __str__(self):
        return nullStr(self.shop) + ", Offer name:- " + nullStr(self.offer_name)


class Offer_Product(models.Model):
    product_name = models.CharField(max_length=255)
    capacity_type = models.CharField(max_length=100, choices=[(
        tag.value, tag) for tag in CapacityTypeChoice.all()])
    local_offer = models.ForeignKey(LocalOffer, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return nullStr(self.product_name)


class LocalOffer_Image(models.Model):
    image = models.ImageField(upload_to='media/image/local_offer')
    timestamp = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(
        Offer_Product, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        new_image = compress(self.image)
        self.image = new_image
        super().save(*args, **kwargs)

    def __str__(self):
        return nullStr(self.image.name)


class LocalOffer_Video(models.Model):
    video = models.FileField(upload_to='media/video/local_offer')
    thumbnail = models.ImageField(
        upload_to='media/video/thumbnail/local_offer')
    timestamp = models.DateTimeField(auto_now_add=True)
    local_offer = models.ForeignKey(LocalOffer, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return nullStr(self.video.name)


class Offer_Discount(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=7)
    number = models.IntegerField()
    discount_type = models.CharField(max_length=100, choices=[
                                     (tag.value, tag) for tag in DiscountChoice.all()])
    product = models.ForeignKey(
        Offer_Product, on_delete=models.CASCADE, null=True)
    sold = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return nullStr(self.price) + " - " + nullStr(self.number)


class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_reg = models.ForeignKey(EventRegistration, on_delete=models.CASCADE)
    invoice_no = models.CharField(
        max_length=50, default=None, blank=True, null=True)
    gst_no_our = models.CharField(
        max_length=50, default=None, blank=True, null=True)
    gst_no_org = models.CharField(
        max_length=50, default=None, blank=True, null=True)
    gross_amount = models.DecimalField(decimal_places=2, max_digits=7)
    trans_date = models.DateTimeField(auto_now_add=True)
    gst_rate = models.DecimalField(decimal_places=2, max_digits=7)
    gst_amount = models.DecimalField(decimal_places=2, max_digits=7)
    commission_rate = models.DecimalField(decimal_places=2, max_digits=7)
    commission_amount = models.DecimalField(decimal_places=2, max_digits=7)
    net_amount = models.DecimalField(decimal_places=2, max_digits=7)
    status = models.CharField(
        max_length=50, default=None, blank=True, null=True)

    def __str__(self):
        return nullStr(self)


class UserBankDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank_name = models.CharField(
        max_length=150, default=None, blank=True, null=True)
    gst_number = models.CharField(
        max_length=50, default=None, blank=True, null=True)
    Account_number = models.CharField(
        max_length=50, default=None, blank=True, null=True)
    ifsc_code = models.CharField(
        max_length=50, default=None, blank=True, null=True)
    name = models.CharField(
        max_length=100, default=None, blank=True, null=True)
    branch_name = models.CharField(
        max_length=50, default=None, blank=True, null=True)
    mobile_number = models.CharField(
        max_length=50, default=None, blank=True, null=True)
    insert_date = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    is_active = models.BooleanField(default=None, blank=True, null=True)


class Attendee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_reg = models.ForeignKey(EventRegistration, on_delete=models.CASCADE)
    book_on = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(decimal_places=2, max_digits=7)
    payment = models.ForeignKey(PaymentTransaction, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    ticket_count = models.IntegerField(null=True, default=None, blank=True)
    ticket_number = models.CharField(
        max_length=50, default=None, blank=True, null=True)
    is_avail = models.BooleanField(default=None, blank=True, null=True)
    avail_datetime = models.DateTimeField(
        default=datetime.now, blank=True, null=True)


class Ticket(models.Model):
    attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE)
    price_matrix = models.ForeignKey(PriceMatrix, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=7)
    status = models.CharField(max_length=50)
    number = models.IntegerField(null=True, default=None, blank=True)


class Config(models.Model):
    key = models.CharField(max_length=20)
    value = models.CharField(max_length=1000)
    subvalue = models.CharField(max_length=1000)
    morevalue = models.CharField(max_length=1000)


class State(models.Model):
    state = models.CharField(max_length=255)

    def __str__(self):
        return nullStr(self.state)


class City(models.Model):
    city = models.CharField(max_length=255)
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name="+")

    def __str__(self):
        return nullStr(self.state)+" - " + nullStr(self.city)


class LocalOfferBooking(models.Model):
    ticket_number = models.CharField(max_length=50)
    rank_number = models.IntegerField()
    user = models.ForeignKey(User,  on_delete=models.CASCADE)
    local = models.ForeignKey(LocalOffer,  on_delete=models.CASCADE)
    expire = models.DateTimeField()
    is_avail = models.BooleanField()
    avail_datetime = models.DateTimeField()

    def __str__(self):
        return nullStr(self.local)+", ticket number:- " + nullStr(self.ticket_number)


class LocalOfferBookingProducts(models.Model):
    booking = models.ForeignKey(LocalOfferBooking, on_delete=models.CASCADE)
    rank_number = models.IntegerField()
    offer = models.ForeignKey(Offer_Discount,  on_delete=models.CASCADE)
    product = models.ForeignKey(Offer_Product,  on_delete=models.CASCADE)

    def __str__(self):
        return nullStr(self.rank_number)


class Complain(models.Model):
    user = models.ForeignKey(User,  on_delete=models.CASCADE)
    mobile_number = models.CharField(
        max_length=50, default=None, blank=True, null=True)
    email = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    remark = models.CharField(
        max_length=2000, default=None, blank=True, null=True)
    complain_type = models.CharField(
        max_length=100, default=None, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    app_version = models.CharField(max_length=100)


class PosterCategory(models.Model):
    category_name = models.CharField(max_length=250)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return nullStr(self.category_name)


class PosterPriceCategory(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    price = models.DecimalField(decimal_places=2, max_digits=7)

    def __str__(self):
        return nullStr(self.name)+" - " + nullStr(self.price)


class PosterPriceCategoryDiscount(models.Model):
    day = models.IntegerField()
    discount_type = models.CharField(max_length=100, choices=[
                                     (tag.value, tag) for tag in DiscountChoice.all()])
    discount = models.DecimalField(decimal_places=2, max_digits=7)
    price_categorty = models.ForeignKey(
        PosterPriceCategory,  on_delete=models.CASCADE,)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return nullStr(self.day)+" - " + nullStr(self.discount_type)+" - "+nullStr(self.discount)


class PosterMaster(models.Model):
    thumnail = models.ImageField(upload_to='media/buy/poster/thumnail')
    svg = models.FileField(upload_to='media/buy/poster/svg')
    price_categorty = models.ForeignKey(
        PosterPriceCategory,  on_delete=models.CASCADE,)
    category = models.ForeignKey(PosterCategory,  on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    default_discount = models.DecimalField(decimal_places=2, max_digits=7)
    discount_type = models.CharField(max_length=100, choices=[
                                     (tag.value, tag) for tag in DiscountChoice.all()])
    content_text = models.CharField(max_length=100, null=True)

    def __str__(self):
        return nullStr(self.svg)


class PosterTransaction(models.Model):
    user = models.ForeignKey(User,  on_delete=models.CASCADE)
    local = models.ForeignKey(LocalOffer,  on_delete=models.CASCADE)
    poster = models.ForeignKey(PosterMaster,  on_delete=models.CASCADE)
    net_amount = models.DecimalField(decimal_places=2, max_digits=7)
    gross_amount = models.DecimalField(decimal_places=2, max_digits=7)
    discount_amount = models.DecimalField(decimal_places=2, max_digits=7)
    discount = models.DecimalField(decimal_places=2, max_digits=7)
    discount_type = models.CharField(max_length=100, choices=[
                                     (tag.value, tag) for tag in DiscountChoice.all()])
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    our_payment_id = models.CharField(
        max_length=40, unique=True, blank=True, null=True)
    razorpay_payment_id = models.CharField(
        max_length=200, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=200, blank=True, null=True)
    display_discount = models.DecimalField(decimal_places=2, max_digits=7)
    display_discount_type = models.CharField(
        max_length=100, choices=[(tag.value, tag) for tag in DiscountChoice.all()])
    display_content_text = models.CharField(max_length=100, null=True)
    coin_used = models.IntegerField(null=True)
    coin_used_amount = models.DecimalField(
        decimal_places=2, max_digits=7, null=True)

    def __str__(self):
        return nullStr(self.our_payment_id)


class AdvertisementMaster(models.Model):
    brand_logo = models.ImageField(upload_to='media/ads/brandlogo')
    brand_name = models.CharField(max_length=200)
    campaign_title = models.CharField(max_length=200)
    call_to_action = models.CharField(max_length=200)
    poster = models.CharField(max_length=2000)
    poster_type = models.CharField(max_length=50)
    thumbnail = models.CharField(max_length=2000)
    ad_clickURL = models.CharField(max_length=2000)
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()
    rank = models.IntegerField(blank=False, null=False, db_index=True)
    is_active = models.BooleanField(default=True)
    app_place = models.CharField(max_length=100)
    duration_in_second = models.IntegerField(
        blank=False, null=False, db_index=True)

    def __str__(self):
        return nullStr(self.brand_name) + " - " + nullStr(self.campaign_title)


class AdTransactionSummary(models.Model):
    ad = models.ForeignKey(AdvertisementMaster, on_delete=models.CASCADE)
    count = models.IntegerField()
    last_use = models.DateTimeField(auto_now=True)

    def __str__(self):
        return nullStr(self.ad)


class AdTransactionDetail(models.Model):
    ad = models.ForeignKey(AdvertisementMaster, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    on_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return nullStr(self.ad)


class CoinSummaryLedger(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_coin = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    redeem_coin = models.IntegerField()
    redeem_amount = models.DecimalField(decimal_places=2, max_digits=7)


class CoinLedgerChoice(Enum):
    login = "LOGIN"
    login_refer = "LOGIN_REFER"
    refered = "REFERED"
    redeem = "REDEEM"
    poster_redeem = "POSTER_REDEEM"
    coin_send = "COIN_SEND"
    coin_receive = "COIN_RECEIVE"

    @classmethod
    def all(cls):
        return [CoinLedgerChoice.login,
                CoinLedgerChoice.login_refer,
                CoinLedgerChoice.refered,
                CoinLedgerChoice.redeem,
                CoinLedgerChoice.poster_redeem,
                CoinLedgerChoice.coin_send,
                CoinLedgerChoice.coin_receive]


class CoinTransType(Enum):
    debit = "DEBIT"
    credit = "CREDIT"

    @classmethod
    def all(cls):
        return [CoinTransType.debit, CoinTransType.debit]


class CoinRedeemStatus(Enum):
    init = "INIT"
    processing = "PROCESSING"
    failed = "FAILED"
    successful = "SUCCESSFULL"

    @classmethod
    def all(cls):
        return [CoinRedeemStatus.init, CoinRedeemStatus.processing, CoinRedeemStatus.failed, CoinRedeemStatus.successful]


class CoinLedger(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    number_of_coin = models.IntegerField()
    trans_timestamp = models.DateTimeField(auto_now=True)
    receive_from = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE, related_name='%(class)s_receive_from')
    receive_on_behalf = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE, related_name='%(class)s_receive_on_behalf')
    type = models.CharField(max_length=100, choices=[(
        tag.value, tag) for tag in CoinLedgerChoice.all()])
    trans_type = models.CharField(max_length=100, choices=[
                                  (tag.value, tag) for tag in CoinTransType.all()])
    redeem_upi = models.CharField(max_length=500, blank=True, null=True)
    redeem_status = models.CharField(max_length=100, choices=[(
        tag.value, tag) for tag in CoinRedeemStatus.all()])
    remark = models.CharField(max_length=2000, blank=True, null=True)
    transcation_number = models.CharField(
        max_length=1000, blank=True, null=True)


class ChatBot(models.Model):
    sender = models.ForeignKey(
        User, related_name='sender', on_delete=models.CASCADE)
    message = models.TextField(max_length=5000, blank=True)
    reply = models.TextField(max_length=5000, blank=True)
    timestamp = models.DateTimeField(auto_now=True)


class LiveStream(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=255, blank=False, null=False)
    event_category = models.CharField(max_length=100, blank=False, null=False)
    event_description = models.TextField(blank=False, null=False)
    start_date = models.DateField(blank=False, null=False)
    start_time = models.TimeField(blank=False, null=False)
    end_time = models.TimeField(blank=False, null=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return nullStr(self.event_name)


class HelpAndFaqs(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return nullStr(self.title)


class Marketing(models.Model):
    title = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='media/image/marketing',
                              default='/media/image/marketing/default.png', blank=True)
    time = models.TimeField(blank=False, null=False)
    date = models.DateField(blank=False, null=False)
    description = models.TextField()
    is_delivary = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # def save(self, *args, **kwargs):
    #     new_image = compress(self.photo)
    #     self.photo = new_image
    #     super().save(*args, **kwargs)

    def __str__(self):
        return nullStr(self.title)


NOTIFICATION_TYPE = (
    ('1', 'SMS'),
    ('2', 'NOTIFICATION'),
    ('3', 'EMAIL'),
)


class NotificationData(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField(max_length=5000, blank=True)
    image = models.FileField(
        max_length=255, upload_to='media/image/notification', blank=True)
    notification_type = models.CharField(
        max_length=10, choices=NOTIFICATION_TYPE, default=1)
    forwhat = models.CharField(max_length=255, null=True, blank=True)
    date_time = models.DateTimeField(null=True, blank=True)


NOTIFICATION_STATUS = (
    ('1', 'panding'),
    ('2', 'send')
)


class Notification(models.Model):
    # notificationid = models.ForeignKey(NotificationData, related_name="NotificationData", on_delete=models.RESTRICT)
    user = models.ForeignKey(
        User, related_name="Notification", on_delete=models.CASCADE)
    userIds = models.TextField(max_length=50000, null=True)
    status = models.CharField(
        max_length=10, choices=NOTIFICATION_STATUS, default=1)
    selected_page = models.TextField(max_length=5000, null=True)
    notification_type = models.TextField(max_length=50000, null=True)
    notification_title = models.TextField(max_length=5000, null=True)
    notification_text = models.TextField(max_length=5000, null=True)
    notification_img = models.FileField(
        max_length=255, upload_to='media/image/notification', blank=True)


class OrganizerEventVideo(models.Model):
    user = models.ForeignKey(
        User, related_name='organizereventvideo', on_delete=models.CASCADE)
    video = models.FileField(upload_to='media/video/organizereventvideo')
    thumbnail = models.ImageField(
        upload_to='media/video/thumbnail/organizereventvideo')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


def is_svg(file):
    tag = None
    # with open(filename, "r") as f:
    try:
        for event, el in et.iterparse(file, ('start',)):
            tag = el.tag
            break
    except et.ParseError:
        pass
    return tag == '{http://www.w3.org/2000/svg}svg'


def validate_svg(file):
    if not is_svg(file):
        raise ValidationError("File not svg")


class SeatingArrangementMaster(models.Model):
    name = models.CharField(max_length=200)
    svg = models.FileField(
        upload_to='media/image/events/seating_arrangement', validators=[validate_svg])
    timestamp = models.DateTimeField(auto_now_add=True)
    sequence = models.IntegerField(null=True, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SeatVerticalLocationChoice(Enum):
    top = "TOP"
    center = "CENTER"
    bottom = "BOTTOM"

    @classmethod
    def all(cls):
        return [SeatVerticalLocationChoice.top, SeatVerticalLocationChoice.center, SeatVerticalLocationChoice.bottom]


class SeatHorizontalLocationChoice(Enum):
    none = "NONE"
    left = "LEFT"
    right = "RIGHT"

    @classmethod
    def all(cls):
        return [SeatHorizontalLocationChoice.none, SeatHorizontalLocationChoice.left, SeatHorizontalLocationChoice.right]


class SeatFoodChoice(Enum):
    veg = "VEG"
    nonveg = "NONVEG"
    both = "BOTH"
    none = "NONE"

    @classmethod
    def all(cls):
        return [SeatFoodChoice.veg, SeatFoodChoice.nonveg, SeatFoodChoice.both, SeatFoodChoice.none]


class BookingAcceptance(Enum):
    pertable = "PERTABLE"
    perperson = "PERPERSON"

    @classmethod
    def all(cls):
        return [BookingAcceptance.pertable, BookingAcceptance.perperson]


class SeatingArrangementBooking(models.Model):
    seat = models.ForeignKey(SeatingArrangementMaster,
                             on_delete=models.CASCADE)
    occasion = models.ForeignKey(EventRegistration, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)

    no_of_seat = models.IntegerField()
    seat_location = models.CharField(max_length=100, choices=[(
        tag.value, tag) for tag in SeatVerticalLocationChoice.all()])
    seat_side = models.CharField(max_length=100, choices=[(
        tag.value, tag) for tag in SeatHorizontalLocationChoice.all()])
    table_person_capacity = models.IntegerField(null=True, blank=True)
    person_capacity = models.IntegerField(null=True, blank=True)
    table_price = models.IntegerField(null=True, blank=True)
    price_per_seat = models.DecimalField(decimal_places=2, max_digits=7)
    total_booking_count = models.IntegerField(null=True)
    description = models.CharField(max_length=2000, null=True, blank=True)
    booking_acceptance = models.CharField(
        max_length=100, choices=[(tag.value, tag) for tag in BookingAcceptance.all()])

    seat_food = models.CharField(max_length=100, choices=[(
        tag.value, tag) for tag in SeatFoodChoice.all()])
    seat_food_description = models.CharField(
        max_length=2000, null=True, blank=True)

    seat_equipment = models.BooleanField(default=False)
    seat_equipment_description = models.CharField(
        max_length=2000, null=True, blank=True)

    def __str__(self):
        return self.seat.name


class FrequentlyAskedQuestions(models.Model):
    question = models.CharField(max_length=512)
    answer = models.CharField(max_length=2000)
    is_active = models.BooleanField(default=True)
    sequence = models.IntegerField(null=True)
    timestampe = models.DateTimeField(auto_now_add=True,)
    start_date = models.DateTimeField(auto_now_add=True, null=True)
    end_date = models.DateTimeField(null=True)


class WishlistOccation(models.Model):
    occasion = models.ForeignKey(
        EventRegistration, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    timestampe = models.DateTimeField(auto_now_add=True,)


class WishlistOffer(models.Model):
    offer = models.ForeignKey(LocalOffer, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    timestampe = models.DateTimeField(auto_now_add=True,)


class CommentsAndRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=22, decimal_places=16, default=0.0)
    avg_rating = models.DecimalField(
        max_digits=22, decimal_places=16, default=0.0)
    user_rating = models.DecimalField(
        max_digits=22, decimal_places=16, default=0.0)
    avg_user_rating = models.DecimalField(
        max_digits=22, decimal_places=16, default=0.0)
    title = models.CharField(max_length=254, blank=False, null=False)
    review = models.CharField(max_length=2000, blank=True, null=True)
    occasion = models.ForeignKey(
        EventRegistration, on_delete=models.CASCADE, null=True)
    offer = models.ForeignKey(LocalOffer, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_replay = models.BooleanField(default=False)
    replay_title = models.CharField(max_length=254, blank=False, null=False)
    replay_review = models.CharField(max_length=2000, blank=True, null=True)
    replay_timestamp = models.DateTimeField(auto_now_add=True)
    replay_persion = models.CharField(max_length=254, blank=False, null=False)
    is_active = models.BooleanField(default=True)


class OurProduct(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    current_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    timestampe = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Topic(models.Model):
    product = models.ForeignKey(
        OurProduct, related_name="topic", on_delete=models.CASCADE)
    link = models.CharField(max_length=255, blank=True, null=True)
    icon = models.ImageField(
        upload_to='media/image/product/icon', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    timestampe = models.DateTimeField(auto_now_add=True)
