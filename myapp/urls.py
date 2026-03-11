from django.urls import path
from . import views

urlpatterns = [
    path('', views.auth , name="auth"),  # الصفحة الرئيسية أصبحت auth
    path('home/', views.home , name="home"),  # الصفحة الرئيسية القديمة أصبحت home
    path('logout/', views.logoutuser , name="logout"),  # الصفحة 
    path('reg/', views.registerUser , name="reg"),  # الصفحة 
]