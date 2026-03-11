import os
import sys
import django
from django.core.management import call_command

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def handler(event, context):
    """دالة Vercel Serverless Function لتشغيل الترحيلات"""
    try:
        # تشغيل migrate
        call_command('migrate')
        return {
            'statusCode': 200,
            'body': 'Migrations completed successfully'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Migrations failed: {str(e)}'
        }
