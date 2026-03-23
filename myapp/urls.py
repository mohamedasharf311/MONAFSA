from django.urls import path
from . import views

urlpatterns = [
    path('', views.auth , name="auth"),  # الصفحة الرئيسية أصبحت auth
    path('home/', views.home , name="home"),  # الصفحة الرئيسية القديمة أصبحت home
    path('logout/', views.logoutuser , name="logout"),  # الصفحة 
    path('reg/', views.registerUser , name="reg"),
    path('api/workers', views.api_workers, name='api_workers'),
    path('api/queue', views.api_queue, name='api_queue'),
    path('api/worker_queue', views.api_worker_queue, name='api_worker_queue'),
    path('api/add_customer', views.api_add_customer, name='api_add_customer'),
    path('api/update_customer_status', views.api_update_customer_status, name='api_update_customer_status'),
    path('api/send_notification', views.api_send_notification, name='api_send_notification'),
    path('api/sync_data', views.api_sync_data, name='api_sync_data'),
    path('api/stats', views.api_stats, name='api_stats'),
    path('api/sync_save', views.api_sync_save, name='api_sync_save'),
    path('api/clear_data', views.api_clear_data, name='api_clear_data'),
    path('api/debug', views.api_debug, name='api_debug'),
    path('api/clear_session', views.api_clear_session, name='api_clear_session'),
# الpath('api/error_test', views.api_error_test, name='api_error_test'),
]
