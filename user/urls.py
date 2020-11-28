from django.urls import path, include

from user import views

app_name = 'user'

urlpatterns = [
    path('register/', views.register, name="register"),
    path('verify/<username>/', views.verify_email, name="verify-email"),
    path('verify/<username>/<token>/<int:code>/', views.auto_verify_email, 
        name="auto-verify-email"),
    path('u/<int:pk>/', views.UserDetail.as_view(), name="profile"),
    path('u/<username>/edit/', views.edit_profile, name='edit-profile'),

]