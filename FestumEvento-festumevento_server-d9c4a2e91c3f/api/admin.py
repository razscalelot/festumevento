from tokenize import Token
from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django.urls import reverse

# Register your models here.

def linkify(field_name):
    """
    Converts a foreign key value into clickable links.
    
    If field_name is 'parent', link text will be str(obj.parent)
    Link will be admin url for the admin url for obj.parent.id:change
    """
    def _linkify(obj):
        linked_obj = getattr(obj, field_name)
        if linked_obj is None:
            return '-'
        app_label = linked_obj._meta.app_label
        model_name = linked_obj._meta.model_name
        view_name = f'admin:{app_label}_{model_name}_change'
        link_url = reverse(view_name, args=[linked_obj.pk])
        return format_html('<a href="{}">{}</a>', link_url, linked_obj)

    _linkify.short_description = field_name  # Sets column name
    return _linkify

class CustomModelAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        dlist = []
        for field in model._meta.fields:
            if field.is_relation == True:
               dlist.append(linkify(field_name=field.name))
            else:
                dlist.append(field.name)

        self.list_display = dlist
        #self.list_display = [field.name for field in model._meta.fields if field.name != "id"]
        #self.list_display_links = [field.name for field in model._meta.fields if field.is_relation == True]
        super(CustomModelAdmin, self).__init__(model, admin_site)

class CustomAdmin(CustomModelAdmin):
    pass
admin.site.register(Event, CustomAdmin)
admin.site.register(SubscriptionMaster, CustomAdmin)
admin.site.register(PaymentTransaction, CustomAdmin)
admin.site.register(SubscriptionTransaction, CustomAdmin)
admin.site.register(EventRegistration, CustomAdmin)
admin.site.register(PriceMatrix, CustomAdmin)
admin.site.register(EventImage, CustomAdmin)
admin.site.register(EventVideo, CustomAdmin)
admin.site.register(LocalOffer, CustomAdmin)
admin.site.register(LocalOffer_Image, CustomAdmin)
admin.site.register(LocalOffer_Video, CustomAdmin)
admin.site.register(Invoice, CustomAdmin)
admin.site.register(UserBankDetail, CustomAdmin)
admin.site.register(Offer_Discount, CustomAdmin)
admin.site.register(Offer_Product, CustomAdmin)
admin.site.register(Attendee, CustomAdmin)
admin.site.register(Ticket, CustomAdmin)
admin.site.register(Config, CustomAdmin)
admin.site.register(State, CustomAdmin)
admin.site.register(City, CustomAdmin)
admin.site.register(LocalOfferBooking, CustomAdmin)
admin.site.register(Complain, CustomAdmin)
admin.site.register(ShopCategory, CustomAdmin)
admin.site.register(Shop, CustomAdmin)
admin.site.register(PosterCategory, CustomAdmin)
admin.site.register(PosterPriceCategory, CustomAdmin)
admin.site.register(PosterMaster, CustomAdmin)
admin.site.register(PosterPriceCategoryDiscount, CustomAdmin)
admin.site.register(AdvertisementMaster, CustomAdmin)
admin.site.register(AdTransactionSummary, CustomAdmin)
admin.site.register(AdTransactionDetail, CustomAdmin)

admin.site.register(CoinSummaryLedger, CustomAdmin)
admin.site.register(CoinLedger, CustomAdmin)
admin.site.register(ChatBot, CustomAdmin)
admin.site.register(LiveStream, CustomAdmin)
admin.site.register(HelpAndFaqs, CustomAdmin)
admin.site.register(Marketing, CustomAdmin)
admin.site.register(NotificationData, CustomAdmin)
admin.site.register(Notification, CustomAdmin)
admin.site.register(OrganizerEventVideo, CustomAdmin)
admin.site.register(SeatingArrangementMaster, CustomAdmin)
admin.site.register(SeatingArrangementBooking, CustomAdmin)
admin.site.register(FrequentlyAskedQuestions, CustomAdmin)
admin.site.register(WishlistOccation, CustomAdmin)
admin.site.register(WishlistOffer, CustomAdmin)
admin.site.register(CommentsAndRating, CustomAdmin)
admin.site.register(OurProduct, CustomAdmin)
admin.site.register(Topic, CustomAdmin)
admin.site.register(OrgEquipment)
