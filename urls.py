from django.urls import path

from apps.account import views
from apps.account.views import ChangePasswordView, profile, profileRoot, ChangePasswordViewRoot

urlpatterns = [
    path('register/', views.register, name='register'),
    path('password-change/', ChangePasswordView.as_view(), name='password_change'),
    path('password-change/root/<int:pk>', ChangePasswordViewRoot.as_view(), name='password_changeRoot'),
    path('user-change/', profile, name='user_change'),
    path('user-change/<int:pk>', profileRoot, name='user_changeRoot'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path("password-reset/", views.MyPasswordResetView.as_view(), name="my_password_reset"),


]
