from django.db import models

# Create your models here.

# models.py - أضف هذه الموديلات بعد موديل User

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class BarberWorker(models.Model):
    """نموذج الصنايعي"""
    STATUS_CHOICES = [
        ('available', 'متاح'),
        ('busy', 'مشغول'),
    ]
    
    name = models.CharField(max_length=50, unique=True, verbose_name="الاسم")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="الحالة")
    current_customer_id = models.BigIntegerField(null=True, blank=True, verbose_name="العميل الحالي")
    skills = models.JSONField(default=list, verbose_name="المهارات")
    queue = models.JSONField(default=list, verbose_name="قائمة الانتظار")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'صنايعي'
        verbose_name_plural = 'الصنايعية'
        ordering = ['name']


class BarberCustomer(models.Model):
    """نموذج العميل"""
    STATUS_CHOICES = [
        ('waiting', 'في الانتظار'),
        ('in_service', 'قيد الخدمة'),
        ('completed', 'مكتمل'),
    ]
    
    # المعرف الخاص (رقم فريد)
    customer_id = models.BigIntegerField(unique=True, verbose_name="رقم العميل")
    
    # معلومات العميل
    name = models.CharField(max_length=100, verbose_name="الاسم")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم الهاتف")
    service = models.CharField(max_length=50, verbose_name="الخدمة")
    worker = models.CharField(max_length=50, verbose_name="الصنايعي")
    
    # معلومات الدور
    queue_number = models.IntegerField(verbose_name="رقم الدور")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting', verbose_name="الحالة")
    
    # تواريخ
    booking_time = models.DateTimeField(auto_now_add=True, verbose_name="وقت الحجز")
    original_order = models.BigIntegerField(verbose_name="الترتيب الأصلي")
    completed_time = models.DateTimeField(null=True, blank=True, verbose_name="وقت الإكمال")
    
    def __str__(self):
        return f"{self.name} - دور {self.queue_number}"
    
    class Meta:
        verbose_name = 'عميل'
        verbose_name_plural = 'العملاء'
        ordering = ['queue_number']


class BarberSettings(models.Model):
    """إعدادات الصالون"""
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.key
    
    class Meta:
        verbose_name = 'إعداد'
        verbose_name_plural = 'الإعدادات'
