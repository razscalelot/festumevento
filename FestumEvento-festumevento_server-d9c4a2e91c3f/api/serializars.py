# from dataclasses import fields
from asyncio import events
from dataclasses import fields
from rest_framework import serializers
from .models import *
from users.models import User
from users.serializers import UserSerializer
from datetime import date, timedelta
import uuid


def Tran_number(self):
    #default = 450000000
    return uuid.uuid4().hex
    # if no is None:
    #   return 450000001
    # else:
    #    return str(default + no + 1)


class PaymentTransactionSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(allow_blank=True, write_only=True)
    our_payment_id = serializers.CharField(allow_blank=True, read_only=True)

    # user = serializers.CharField(allow_blank=True)

    class Meta:
        model = PaymentTransaction
        fields = ('amount', 'status', 'user_phone', 'our_payment_id')

    def create(self, validated_data):
        user_phone = validated_data.pop('user_phone')
        user_instance = User.objects.get(mobile=user_phone)
        payment_id = Tran_number(self)
        pt = PaymentTransaction.objects.create(**validated_data,
                                               our_payment_id=payment_id, user=user_instance)
        return pt


class SubscriptionMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionMaster
        fields = ("id", "price", "no_of_post", "max_days",
                  "name", "validity_days", "is_active")


class SubscriptionTransactionSerializer(serializers.ModelSerializer):
    subscription_id = serializers.IntegerField(write_only=True)
    user_phone = serializers.CharField(write_only=True)
    our_payment_id = serializers.CharField(write_only=True)

    price = serializers.DecimalField(
        decimal_places=2, max_digits=7, allow_null=True, read_only=True)
    no_of_post = serializers.IntegerField(allow_null=True, read_only=True)
    used_post = serializers.IntegerField(allow_null=True, read_only=True)
    max_days = serializers.IntegerField(allow_null=True, read_only=True)
    used_days = serializers.IntegerField(allow_null=True, read_only=True)
    name = serializers.CharField(allow_blank=True, read_only=True)
    start_date = serializers.DateField(
        allow_null=True, read_only=True, format='%d %b %Y')
    end_date = serializers.DateField(
        allow_null=True, read_only=True, format='%d %b %Y')
    is_active = serializers.BooleanField(allow_null=True, read_only=True)
    timestamp = serializers.DateTimeField(
        allow_null=True, read_only=True, format='%d %b %Y')
    payment_status = serializers.CharField(allow_blank=True, read_only=True)
    subscription = SubscriptionMasterSerializer(read_only=True)

    class Meta:
        model = SubscriptionTransaction
        fields = ('id', 'price', 'no_of_post', 'used_post', 'max_days', 'used_days', 'name',
                  'start_date', 'end_date', 'payment_status', 'is_active', 'timestamp', 'subscription',
                  'subscription_id', 'user_phone', 'our_payment_id')

    def create(self, validated_data):
        user_phone = validated_data.pop('user_phone')
        user_instance = User.objects.get(mobile=user_phone)
        subscription_id = validated_data.pop('subscription_id')

        subscription_instance = SubscriptionMaster.objects.get(
            id=subscription_id)
        price = subscription_instance.price
        no_of_post = subscription_instance.no_of_post
        used_post = 0
        max_days = subscription_instance.max_days
        used_days = 0
        name = subscription_instance.name
        start_date = date.today().strftime('%Y-%m-%d')
        end_date = (date.today(
        ) + timedelta(days=subscription_instance.validity_days)).strftime('%Y-%m-%d')
        timestamp = date.today().strftime('%Y-%m-%d %H:%M')
        payment_id = validated_data.pop('our_payment_id')
        payment = PaymentTransaction.objects.get(our_payment_id=payment_id)

        payment_status = payment.status

        st = SubscriptionTransaction.objects.create(**validated_data,
                                                    subscription=subscription_instance,
                                                    price=price,
                                                    no_of_post=no_of_post,
                                                    used_post=used_post,
                                                    max_days=max_days,
                                                    used_days=used_days,
                                                    name=name,
                                                    start_date=start_date,
                                                    end_date=end_date,
                                                    user=user_instance,
                                                    payment_status=payment_status,
                                                    payment=payment,
                                                    timestamp=timestamp
                                                    )

        return st


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = "__all__"


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = "__all__"


class EventCompanyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCompanyImage
        fields = '__all__'
        extra_kwargs = {'id': {'read_only': True}}


class EventCompanyVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCompanyVideo
        fields = '__all__'
        extra_kwargs = {'id': {'read_only': True}}


class EventCompanyDetailsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()

    @staticmethod
    def get_image(obj):
        image_id = EventCompanyImage.objects.filter(company_id=obj.id)
        image = EventCompanyImageSerializer(image_id, many=True)
        return image.data

    @staticmethod
    def get_video(obj):
        video_id = EventCompanyVideo.objects.filter(company_id=obj.id)
        video = EventCompanyVideoSerializer(video_id, many=True)
        return video.data

    class Meta:
        model = EventCompanyDetails
        fields = ('id', 'event_reg', 'name', 'gst', 'contact_no', 'email', 'about', 'flat_no',
                  'street', 'area', 'city', 'state', 'pincode', 'image', 'video')
        extra_kwargs = {'id': {'read_only': True}}


class EventPersonalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPersonalDetails
        fields = '__all__'
        extra_kwargs = {'id': {'read_only': True}}


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ('id', 'name', 'event_type', 'event_category',
                  'is_other', 'user', 'is_active')


class EventRegistrationSerializer(serializers.ModelSerializer):
    # event = EventSerializer(read_only=True)

    class Meta:
        model = EventRegistration
        fields = ('id', 'event', 'location_type', 'occupancy_type', 'capacity', 'location_address',
                  'address', 'poster', 'start_date', 'end_date', 'start_time', 'end_time', 'flat_no', 'street_name', 'area_name', 'accept_booking', 'orgdiscountsId',
                  'city', 'state', 'pincode', 'longitude', 'latitude',
                  'permission_letter', 'event', 'status', 'is_verify', 'is_active', 'description', 'sold', 'is_food', 'food_type', 'food_description', 'is_equipment', 'equipment_description', 't_and_c', 'facebook', 'twitter', 'youtube', 'pinterest', 'instagram', 'linkedin')


class EventRegistrationSerializer2(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    occasion = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    occasion_id = serializers.SerializerMethodField()
    companydetails = serializers.SerializerMethodField()
    personaldetails = serializers.SerializerMethodField()
    discount_id = serializers.SerializerMethodField()
    # singal_event = serializers.SerializerMethodField('_user')

    start_date = serializers.DateField(
        allow_null=True, read_only=True, format='%d %b %Y')
    end_date = serializers.DateField(
        allow_null=True, read_only=True, format='%d %b %Y')
    start_time = serializers.TimeField(
        allow_null=True, read_only=True, format='%I:%M %p')
    end_time = serializers.TimeField(
        allow_null=True, read_only=True, format='%I:%M %p')

    # def _user(self, obj):
    #     request = self.context.get('request', None)
    #     event_id = Event.objects.filter(user_id=request._user.id)
    #     singal_event = EventSerializer(event_id, many=True)
    #     return singal_event.data

    @staticmethod
    def get_occasion_id(obj):
        occasion = CommentsAndRating.objects.filter(occasion_id=obj.id)
        occasion_id = CommentsAndRatingSerializer(occasion, many=True)
        return occasion_id.data

    @staticmethod
    def get_discount_id(obj):
        discount = OrgDiscounts.objects.filter(
            orgdiscountsId=obj.orgdiscountsId_id)
        discount_id = OrgDiscountSerializers(discount, many=True)
        return discount_id.data

    @staticmethod
    def get_occasion(obj):
        occasion_id = SeatingArrangementBooking.objects.filter(
            occasion_id=obj.id)
        occasion = SeatingArrangementBookingSerializer(occasion_id, many=True)
        return occasion.data

    @staticmethod
    def get_companydetails(obj):
        companydetails_id = EventCompanyDetails.objects.filter(
            event_reg=obj.id)
        companydetails = EventCompanyDetailsSerializer(
            companydetails_id, many=True)
        return companydetails.data

    @staticmethod
    def get_personaldetails(obj):
        personaldetails_id = EventPersonalDetails.objects.filter(
            event_reg=obj.id)
        companydetails = EventPersonalDetailsSerializer(
            personaldetails_id, many=True)
        return companydetails.data

    @staticmethod
    def get_image(obj):
        image_id = EventImage.objects.filter(event_reg_id=obj.id)
        image = EventImageSerializer(image_id, many=True)
        return image.data

    @staticmethod
    def get_video(obj):
        video_id = EventVideo.objects.filter(event_reg_id=obj.id)
        video = EventVideoSerializer(video_id, many=True)
        return video.data

    class Meta:
        model = EventRegistration
        fields = ('id', 'location_type', 'occupancy_type', 'discount_id', 'occasion_id', 'occasion', 'companydetails', 'personaldetails', 'capacity', 'location_address',
                  'address', 'poster', 'start_date', 'end_date', 'start_time', 'end_time', 'accept_booking', 'event',
                  'permission_letter', 'status', 'is_verify', 'is_active', 'description', 'city', 'state', 'pincode', 'longitude', 'latitude', 'sold', 'is_food', 'food_type', 'food_description', 'is_equipment', 'equipment_description', 'image', 'video', 't_and_c', 'facebook', 'twitter', 'youtube', 'pinterest', 'instagram', 'linkedin', 'calender', 'live')


class EventImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventImage
        fields = "__all__"


class EventVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventVideo
        fields = "__all__"


class SeatingArrangementBookingSerializer(serializers.ModelSerializer):
    # timestamp = serializers.DateField(allow_null=True, read_only=True,format='%d %b %Y')
    # seat = SeatingArrangementMasterSerializer(read_only=True)

    class Meta:
        model = SeatingArrangementBooking
        fields = "__all__"


class SeatingArrangementMasterSerializer(serializers.ModelSerializer):
    #timestamp = serializers.DateField(allow_null=True, read_only=True,format='%d %b %Y')
    arrangement = serializers.SerializerMethodField()

    @staticmethod
    def get_arrangement(obj):
        arrangement_id = SeatingArrangementBooking.objects.filter(
            seat_id=obj.id)
        arrangement = SeatingArrangementBookingSerializer(
            arrangement_id, many=True)
        return arrangement.data

    class Meta:
        model = SeatingArrangementMaster
        fields = ('id', 'name', 'svg', 'timestamp',
                  'sequence', 'is_active', 'arrangement')


class SeatingArrangementBookingSerializerInsert(serializers.ModelSerializer):
    #timestamp = serializers.DateField(allow_null=True, read_only=True,format='%d %b %Y')
    #seat = SeatingArrangementBookingSerializer(read_only=True)
    class Meta:
        model = SeatingArrangementBooking
        fields = "__all__"


class OrgEquipmentSerializers(serializers.ModelSerializer):
    class Meta:
        model = OrgEquipment
        fields = '__all__'


class DiscountSerializers(serializers.ModelSerializer):
    class Meta:
        model = Discounts
        fields = '__all__'


class OrgDiscountSerializers(serializers.ModelSerializer):
    orgequipmentdiscounts_id = serializers.SerializerMethodField()

    @staticmethod
    def get_orgequipmentdiscounts_id(obj):
        orgequipmentdiscounts = OrgEquipment.objects.filter(
            orgequipmentdiscounts_id=obj.orgdiscountsId)
        orgequipmentdiscounts_id = OrgEquipmentSerializers(
            orgequipmentdiscounts, many=True)
        return orgequipmentdiscounts_id.data

    class Meta:
        model = OrgDiscounts
        fields = ('orgdiscountsId', 'orguser', 'orgdiscount_id',
                  'orgdiscount', 'orgdescription', 'orgequipmentdiscounts_id')


class OrgEventRegistrationSerializer(serializers.ModelSerializer):
    occasion = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    # city = serializers.SerializerMethodField()
    # state = serializers.SerializerMethodField()
    occasion_id = serializers.SerializerMethodField()
    companydetails = serializers.SerializerMethodField()
    personaldetails = serializers.SerializerMethodField()
    discount_id = serializers.SerializerMethodField()

    start_date = serializers.DateField(
        allow_null=True, read_only=True, format='%d %b %Y')
    end_date = serializers.DateField(
        allow_null=True, read_only=True, format='%d %b %Y')
    start_time = serializers.TimeField(
        allow_null=True, read_only=True, format='%I:%M %p')
    end_time = serializers.TimeField(
        allow_null=True, read_only=True, format='%I:%M %p')

    @staticmethod
    def get_occasion_id(obj):
        occasion = CommentsAndRating.objects.filter(occasion_id=obj.id)
        print('occasion1', occasion)
        occasion_id = CommentsAndRatingSerializer(occasion, many=True)
        return occasion_id.data

    @staticmethod
    def get_discount_id(obj):
        discount = OrgDiscounts.objects.filter(orgdiscountsId=obj.id)
        discount_id = OrgDiscountSerializers(discount, many=True)
        return discount_id.data

    @staticmethod
    def get_occasion(obj):
        occasion_id = SeatingArrangementBooking.objects.filter(
            occasion_id=obj.id)
        occasion = SeatingArrangementBookingSerializer(occasion_id, many=True)
        return occasion.data

    @staticmethod
    def get_companydetails(obj):
        companydetails_id = EventCompanyDetails.objects.filter(
            event_reg=obj.id)
        companydetails = EventCompanyDetailsSerializer(
            companydetails_id, many=True)
        return companydetails.data

    @staticmethod
    def get_personaldetails(obj):
        personaldetails_id = EventPersonalDetails.objects.filter(
            event_reg=obj.id)
        companydetails = EventPersonalDetailsSerializer(
            personaldetails_id, many=True)
        return companydetails.data

    # @staticmethod
    # def get_city(obj):
    #     city_id = City.objects.filter(id=obj.city)
    #     city = CitySerializer(city_id, many=True)
    #     return city.data

    # @staticmethod
    # def get_state(obj):
    #     state_id = State.objects.filter(id=obj.state)
    #     state = StateSerializer(state_id, many=True)
    #     return state.data

    @staticmethod
    def get_image(obj):
        image_id = EventImage.objects.filter(event_reg_id=obj.id)
        image = EventImageSerializer(image_id, many=True)
        return image.data

    @staticmethod
    def get_video(obj):
        video_id = EventVideo.objects.filter(event_reg_id=obj.id)
        video = EventVideoSerializer(video_id, many=True)
        return video.data

    class Meta:
        model = EventRegistration
        fields = ('id', 'location_type', 'occupancy_type', 'discount_id', 'occasion_id', 'occasion', 'companydetails', 'personaldetails', 'capacity', 'location_address',
                  'address', 'poster', 'start_date', 'end_date', 'start_time', 'end_time', 'accept_booking',
                  'permission_letter', 'status', 'is_verify', 'is_active', 'description', 'city', 'state', 'pincode', 'longitude', 'latitude', 'sold', 'is_food', 'food_type', 'food_description', 'is_equipment', 'equipment_description', 'image', 'video', 't_and_c', 'facebook', 'twitter', 'youtube', 'pinterest', 'instagram', 'linkedin', 'calender', 'live')


class OrgEventSerializer(serializers.ModelSerializer):
    event = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)

    @staticmethod
    def get_event(obj):
        event_id = EventRegistration.objects.filter(event_id=obj.id)
        event = OrgEventRegistrationSerializer(event_id, many=True)
        return event.data

    class Meta:
        model = Event
        fields = ('id', 'name', 'event_type', 'event_category',
                  'is_other', 'user', 'is_active', 'event')


class PriceMatrixSerializer(serializers.ModelSerializer):

    class Meta:
        model = PriceMatrix
        fields = "__all__"


class SocialEventImageSerializer(serializers.ModelSerializer):
    event_reg = EventRegistrationSerializer2(read_only=True)

    class Meta:
        model = EventImage
        fields = "__all__"


class SocialEventVideoSerializer(serializers.ModelSerializer):
    event_reg = EventRegistrationSerializer2(read_only=True)

    class Meta:
        model = EventVideo
        fields = "__all__"


class LocalOfferSerializer(serializers.ModelSerializer):
    #event = EventSerializer(read_only=True)
    #subscription = SubscriptionTransactionSerializer(read_only=True)
    #start_date = serializers.DateField(allow_null=True, read_only=True,format='%d %b %Y')
    #end_date = serializers.DateField(allow_null=True, read_only=True,format='%d %b %Y')

    class Meta:
        model = LocalOffer
        fields = "__all__"


class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = "__all__"


class LocalOfferSerializer2(serializers.ModelSerializer):
    #shop = ShopSerializer(read_only=True)
    #subscription = SubscriptionTransactionSerializer(read_only=True)
    start_date = serializers.DateField(
        allow_null=True, read_only=True, format='%d %b %Y')
    end_date = serializers.DateField(
        allow_null=True, read_only=True, format='%d %b %Y')

    class Meta:
        model = LocalOffer
        fields = "__all__"


class LocalOfferSerializerForUser(serializers.ModelSerializer):
    shop = ShopSerializer(read_only=True)
    #subscription = SubscriptionTransactionSerializer(read_only=True)
    start_date = serializers.DateField(
        allow_null=True, read_only=True, format='%d %b %Y')
    end_date = serializers.DateField(
        allow_null=True, read_only=True, format='%d %b %Y')

    class Meta:
        model = LocalOffer
        fields = "__all__"


class LocalOfferImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocalOffer_Image
        fields = "__all__"


class LocalOfferVideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocalOffer_Video
        fields = "__all__"


class SocialLocalOfferImageSerializer(serializers.ModelSerializer):
    #product = Offer_ProductSerializer(read_only=True)

    class Meta:
        model = LocalOffer_Image
        fields = "__all__"


class SocialLocalOfferVideoSerializer(serializers.ModelSerializer):
    local_offer = LocalOfferSerializerForUser(read_only=True)

    class Meta:
        model = LocalOffer_Video
        fields = "__all__"


class Offer_ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offer_Product
        fields = "__all__"


class Offer_DiscountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offer_Discount
        fields = "__all__"


class ConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = Config
        fields = "__all__"


class LocalOfferBookingSerializer(serializers.ModelSerializer):
    local = LocalOfferSerializerForUser(read_only=True)
    offer = Offer_DiscountSerializer(read_only=True)
    expire = serializers.DateTimeField(
        allow_null=True, read_only=True, format='%d %b %Y')
    avail_datetime = serializers.DateTimeField(
        allow_null=True, read_only=True, format='%d %b %Y')

    class Meta:
        model = LocalOfferBooking
        fields = "__all__"


class LocalOfferBookingSerializer3(serializers.ModelSerializer):
    expire = serializers.DateTimeField(
        allow_null=True, read_only=True, format='%d %b %Y')
    avail_datetime = serializers.DateTimeField(
        allow_null=True, read_only=True, format='%d %b %Y')
    user = UserSerializer(read_only=True)

    class Meta:
        model = LocalOfferBooking
        fields = "__all__"


class LocalOfferBookingSerializer2(serializers.ModelSerializer):
    #local = LocalOfferSerializer2(read_only=True)
    offer = Offer_DiscountSerializer(read_only=True)
    expire = serializers.DateTimeField(
        allow_null=True, read_only=True, format='%d %b %Y')
    avail_datetime = serializers.DateTimeField(
        allow_null=True, read_only=True, format='%d %b %Y')
    user = UserSerializer(read_only=True)
    local = LocalOfferSerializer(read_only=True)

    class Meta:
        model = LocalOfferBooking
        fields = "__all__"


class AttendeeSerializer(serializers.ModelSerializer):
    event_reg = EventRegistrationSerializer2(read_only=True)
    payment = PaymentTransactionSerializer(read_only=True)
    book_on = serializers.DateTimeField(
        allow_null=True, read_only=True, format='%d %b %Y')
    avail_datetime = serializers.DateTimeField(
        allow_null=True, read_only=True, format='%d %b %Y')

    class Meta:
        model = Attendee
        fields = "__all__"


class AttendeeSerializer2(serializers.ModelSerializer):
    #event_reg = EventRegistrationSerializer2(read_only= True)
    payment = PaymentTransactionSerializer(read_only=True)
    book_on = serializers.DateTimeField(
        allow_null=True, read_only=True, format='%d %b %Y')
    avail_datetime = serializers.DateTimeField(
        allow_null=True, read_only=True, format='%d %b %Y')
    user = UserSerializer(read_only=True)

    class Meta:
        model = Attendee
        fields = "__all__"


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    trans_date = serializers.DateTimeField(
        allow_null=True, read_only=True, format='%d %b %Y')

    class Meta:
        model = Invoice
        fields = "__all__"


class ComplainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Complain
        fields = "__all__"


class ShopCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopCategory
        fields = "__all__"


class ShopSerializer(serializers.ModelSerializer):
    category = ShopCategorySerializer(read_only=True)

    class Meta:
        model = Shop
        fields = "__all__"


class ShopSerializer2(serializers.ModelSerializer):
    #category = ShopCategorySerializer(read_only=True)

    class Meta:
        model = Shop
        fields = "__all__"


class LocalOfferBookingProductsSerializer(serializers.ModelSerializer):
    offer = Offer_DiscountSerializer(read_only=True)
    product = Offer_ProductSerializer(read_only=True)

    class Meta:
        model = LocalOfferBookingProducts
        fields = "__all__"


class PosterCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = PosterCategory
        fields = "__all__"


class PosterPriceCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = PosterPriceCategory
        fields = "__all__"


class PosterPriceCategoryDiscountSerializer(serializers.ModelSerializer):

    class Meta:
        model = PosterPriceCategoryDiscount
        fields = "__all__"


class PosterMasterSerializer(serializers.ModelSerializer):
    price_categorty = PosterPriceCategorySerializer(read_only=True)

    class Meta:
        model = PosterMaster
        fields = "__all__"


class PosterTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PosterTransaction
        fields = "__all__"


class AdvertisementMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdvertisementMaster
        fields = "__all__"


class AdTransactionSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = AdTransactionSummary
        fields = "__all__"


class AdTransactionDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdTransactionDetail
        fields = "__all__"


class CoinSummaryLedgerSerializer(serializers.ModelSerializer):

    class Meta:
        model = CoinSummaryLedger
        fields = "__all__"


class CoinLedgerSerializer(serializers.ModelSerializer):
    receive_from = UserSerializer(read_only=True)
    receive_on_behalf = UserSerializer(read_only=True)

    class Meta:
        model = CoinLedger
        fields = "__all__"

# class ChatBotSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = ChatBot
#         fields = "__all__"


class ChatterBotSerializers(serializers.ModelSerializer):
    class Meta:
        model = ChatBot
        fields = "__all__"


class LiveStreamSerializer(serializers.ModelSerializer):
    # start_date = serializers.DateField(read_only=True,format='%d %b %Y')
    # start_time = serializers.TimeField(read_only=True,format='%I:%M %p')
    # end_time = serializers.TimeField(read_only=True, format='%I:%M %p')
    class Meta:
        model = LiveStream
        fields = ('id', 'event_name', 'event_category', 'event_description',
                  'start_date', 'start_time', 'end_time', 'user', 'is_active')


class HelpAndFaqsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpAndFaqs
        fields = "__all__"


class MarketingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marketing
        fields = "__all__"


class OldCustomerDataExcelUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class OldCustomerDataSaveFileSerializer(serializers.Serializer):

    class Meta:
        model = User
        fields = "__all__"


class NotificationDataSerializers(serializers.ModelSerializer):
    class Meta:
        model = NotificationData
        fields = [
            'id',
            'text',
            'image',
            'notification_type',
            'date_time',
            'forwhat'
        ]
        extra_kwargs = {'id': {'read_only': True}}


class NotificationSerializers(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            # 'notificationid',
            'user',
            'userIds',
            'status',
            'selected_page',
            'notification_title',
            'notification_type',
            'notification_text',
            'notification_img',
            'date_time'
        ]
        extra_kwargs = {'id': {'read_only': True}}


class OrganizerEventVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizerEventVideo
        fields = "__all__"


class FrequentlyAskedQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrequentlyAskedQuestions
        fields = "__all__"


class WishlistOccationSerializer(serializers.ModelSerializer):
    occasion = EventRegistrationSerializer2(read_only=True)

    class Meta:
        model = WishlistOccation
        fields = "__all__"


class WishlistOfferSerializer(serializers.ModelSerializer):
    offer = LocalOfferSerializerForUser(read_only=True)

    class Meta:
        model = WishlistOffer
        fields = "__all__"


class ShopCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopCategory
        fields = "__all__"


class CommentsAndRatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CommentsAndRating
        fields = "__all__"


class EventRegistrationSerializerSmall(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    #subscription = SubscriptionTransactionSerializer(read_only=True)
    start_date = serializers.DateField(
        allow_null=True, read_only=True, format='%d %b %Y')
    end_date = serializers.DateField(
        allow_null=True, read_only=True, format='%d %b %Y')
    start_time = serializers.TimeField(
        allow_null=True, read_only=True, format='%I:%M %p')
    end_time = serializers.TimeField(
        allow_null=True, read_only=True, format='%I:%M %p')

    class Meta:
        model = EventRegistration
        fields = ('id', 'location_type', 'occupancy_type',
                  'poster', 'start_date', 'end_date', 'start_time', 'end_time', 'event')


class AttendeeSmallSerializer(serializers.ModelSerializer):
    event_reg = EventRegistrationSerializerSmall(read_only=True)
    #payment = PaymentTransactionSerializer(read_only = False)
    #book_on = serializers.DateTimeField(allow_null=True, read_only=True,format='%d %b %Y')
    #avail_datetime = serializers.DateTimeField(allow_null=True, read_only=True,format='%d %b %Y')
    #user = UserSerializer(read_only=False)

    class Meta:
        model = Attendee
        fields = ('event_reg',)


class ShopSerializerSmall(serializers.ModelSerializer):
    category = ShopCategorySerializer(read_only=True)

    class Meta:
        model = Shop
        fields = ('shop_name', 'category')


class LocalOfferSerializerSmall(serializers.ModelSerializer):
    shop = ShopSerializerSmall(read_only=True)
    #subscription = SubscriptionTransactionSerializer(read_only=True)
    start_date = serializers.DateField(
        allow_null=True, read_only=True, format='%d %b %Y')
    end_date = serializers.DateField(
        allow_null=True, read_only=True, format='%d %b %Y')

    class Meta:
        model = LocalOffer
        fields = ('id', 'shop', 'start_date',
                  'end_date', 'poster', 'offer_name')


class LocalOfferBookingSerializerSmall(serializers.ModelSerializer):
    #expire = serializers.DateTimeField(allow_null=True, read_only=True,format='%d %b %Y')
    #avail_datetime = serializers.DateTimeField(allow_null=True, read_only=True,format='%d %b %Y')
    #user = UserSerializer(read_only=True)
    local = LocalOfferSerializerSmall(read_only=True)

    class Meta:
        model = LocalOfferBooking
        fields = ('local',)


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"


class OurProductSerializer(serializers.ModelSerializer):
    topic = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = OurProduct
        fields = ('id', 'name', 'description', 'current_index', 'topic')
