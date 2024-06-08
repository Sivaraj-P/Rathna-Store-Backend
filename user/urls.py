from django.urls import path
from .views import LoginApiView,UserApiView,ActivateUserApiView,RegenerateActivationTokenApiView,GenerateOTPApiView,ForgetPasswordApiView
from knox.views import LogoutView,LogoutAllView
urlpatterns=[
    path('login',LoginApiView.as_view(),name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logoutall/', LogoutAllView.as_view(), name='logoutall'),
    path('user',UserApiView.as_view(),name='user'),
    path('activate-user/<str:token>',ActivateUserApiView.as_view(),name='activate_user'),
    path('reactivate',RegenerateActivationTokenApiView.as_view(),name='reactivate_user'),
    path('generate-otp',GenerateOTPApiView.as_view(),name='generate_otp'),
    path('forget-password',ForgetPasswordApiView.as_view(),name='forget_password')
]