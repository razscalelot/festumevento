from django.urls import path

from . import views

urlpatterns = [
    path('users/', views.UserListView.as_view()),
    path('user/', views.GetUser.as_view()),
    path('register/', views.UserCreate.as_view(), name='Register'),
    path('login/', views.UserLogin.as_view(), name='login'),
    path('logout/', views.UserLogout.as_view(), name='logout'),
    path('sendOtp/', views.SendOtp.as_view(), name='SendOtp'),
    path('verifyOtp/', views.VerifyOtp.as_view(), name='Verify Otp'),
    path('verifyOtpChangePassword/', views.VerifyOtpChangePassword.as_view(),
         name='Verify Otp Change Password'),
]