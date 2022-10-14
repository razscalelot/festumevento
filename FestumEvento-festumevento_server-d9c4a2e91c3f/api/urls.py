from django.urls import include, path
from django.urls import re_path as url
from . import views
from . import views_new

from rest_auth import urls
urlpatterns = [
    path('authentication/', include('users.urls')),
    #path('authentication/', include('rest_auth.urls')),
    path('payment/', views.Payment.as_view()),
    path('usersubscription/', views.UserSubscription.as_view()),
    path('subscription/', views.SubscriptionMasterView.as_view()),

    # Register Event
    path('event/register/', views.EventRegister.as_view()),
    path('event/edit/<int:id>', views.EventRegister.as_view()),

    # Get all events
    path('events/', views.SetEvent.as_view()),
    path('events/<int:id>', views.SetEvent.as_view()),

    # Get org events 
    path('org/event/', views.OrgEvents.as_view()),
    path('org/event/add', views.OrgEvents.as_view()),
    path('org/event/<int:id>', views.OrgEvents.as_view()),
    path('org/event/delete/<int:id>', views.OrgEvents.as_view()),


    path('discount', views.DiscountView.as_view(), name="DiscountView"),
    path('discount/<int:id>', views.DiscountView.as_view(), name="DiscountView"),

    path('org/discount', views.OrgDiscountView.as_view(), name="DiscountView"),
    path('org/equipment/discount', views.OrgDiscountView.as_view(), name="DiscountView"),
    path('org/discount/<int:id>', views.OrgDiscountView.as_view(), name="DiscountView"),

    
    path('event/image/', views.EventImages.as_view()),
    path('event/video/', views.EventVideos.as_view()),

    path('event/gallery', views.EventGallery.as_view(), name='EventGallery'),

    path('event/companydetail', views.EventCompanyDetailsView.as_view(), name="EventCompanyDetailsView"),
    path('event/companydetail/image', views.EventCompanyImageView.as_view(), name="EventCompanyImageView"),
    path('event/companydetail/video', views.EventCompanyVideoView.as_view(), name="EventCompanyVideoView"),

    path('event/personaldetail', views.EventPersonalDetailsView.as_view(), name="EventPersonalDetailsView"),

    path('event/pricematrix/', views.EventPriceMatrix.as_view()),
    path('event/attendee',views.UserAttendee.as_view()),
    path('local/attendee',views.UserLocalBooking.as_view()),    
    path('event/localoffer/', views.LocalOfferView.as_view()),
    path('event/localoffer/image/', views.LocalOfferImages.as_view()),
    path('event/localoffer/video/', views.LocalOfferVideos.as_view()),
    path('shop',views.ShopView.as_view()),
    path('shop-category', views.ShopCategoryView.as_view()), 
    path('shop-category/<int:id>', views.ShopCategoryView.as_view()), 
    path('event/scan',views.ValidateScan.as_view()),
    path('event/checkin',views.CheckInView.as_view()),
    path('event/checklist',views.CheckInView.as_view()),
    path('event/localoffer/product', views.OfferProductView.as_view()),
    path('event/localoffer/product/discount', views.OfferDiscountView.as_view()),
    path('config/', views.ConfigView.as_view()),
    path('state/', views.StateView.as_view()),
    #path('auth/registration/', views.UserCreate.as_view(), name='account-create'),

    path('user/events/', views.UserEventsView.as_view()),
    path('user/occasion', views.UserGetOccasion.as_view()),
    path('user/locals/', views.UserLocalOffer.as_view()),
    path('user/offer',views.UserGetOffer.as_view()),
    path('user/locals/book', views.BookLocal.as_view()),
    path('user/events/calculate/new', views.PriceCountEvent.as_view()),
    path('user/events/book/new', views.BookEvent.as_view()),
    path('user/bookings', views.UserBooking.as_view()),

    path('event/invoice',views.InvoiceView.as_view()),
    path('bill/generate',views.GenerateBill.as_view()),
    path('social/media',views.VideoAndImages.as_view()),
    path('complain',views.ComplainView.as_view()),

    path('poster/categories',views.PosterCategoryView.as_view()),
    path('poster/categoy/by', views.PosterByCategoryView.as_view()),
    path('poster/change/value', views.PosterValueChangeView.as_view()),
    path('poster/transaction/create', views.PosterTransactionView.as_view()),
    path('poster/transaction/update', views.PosterTransactionUpdateView.as_view()),
    path('poster/transaction/detail', views.PosterTransactionDetailView.as_view()),
    path('advertisement/show', views.AdvertisementMasterView.as_view()),
    path('advertisement/click', views.AdClickView.as_view()),

    path('coin/summary', views.CoinSummaryLedgerView.as_view()),
    path('coin/ledger', views.CoinLedgerView.as_view()),
    path('coin/enable', views.IsToEnableCoinSystem.as_view()),
    path("coin/transaction", views.CoinTransaction.as_view()),
    path("coin/user/transaction", views.TransactionUserCoin.as_view()),
    path('notify/text', views.testNotification.as_view()),
    path('coin/payout', views.RedeemCoin.as_view()),
    
    path('comment/rating',views.CommentsAndRatingView.as_view()),
    path('comment/rating/ask',views.AskCommentsAndRatingView.as_view()),

    path("entertainment/", views.EntertainmentView.as_view()),

    # path('chatbot/', views.ChatBot.as_view()),
    path('chatbot/', views.ChatterBotApiView.as_view()),

    path('live-stream/', views.LiveStreamView.as_view()),
    # path('broadcast/', views.LiveStreamBroadcast.as_view()),

    path('faqs/', views.HelpAndFaqsView.as_view()),
    path('marketing/', views.MarketingView.as_view()),
    path('marketing/pending', views.MarketingPendingView.as_view()),

     #new view paths
    path('faq', views_new.FrequentlyAskedQuestionsView.as_view()),
    path('wishlist/offer/set', views_new.WishlistOfferView.as_view()),
    path('wishlist/occasion/set', views_new.WishlistOccationView.as_view()),
    path('wishlist', views_new.WishlistView.as_view()),
    path('seats', views_new.SeatingArrangementMasterView.as_view()),
    path('seat/booking', views_new.SeatingArrangementBookingView.as_view()),

    path('stream/', views.stream),
    path('old-customer', views.OldCustomerDataView.as_view()),
    path('pushnotification', views.pushnotification),
    path('organizer/event-video', views.OrganizerEventVideoView.as_view()),
    path('organizer/wise/event-video', views.OrganizerUserViseEventVideoView.as_view()),
    path('our-product', views.OurProductView.as_view()),
    path('our-product/topic', views.TopicView.as_view()),
        
    url(r'convert/([0-9]+)$', views.convert),
]
