import os
import sys
import django
from django.core.management import call_command

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def migrate_database():
    """تشغيل الترحيلات"""
    try:
        print("🚀 بدء تشغيل الترحيلات...")
        call_command('migrate')
        print("✅ الترحيلات اكتملت بنجاح")
        return True
    except Exception as e:
        print(f"❌ فشلت الترحيلات: {e}")
        return False

if __name__ == "__main__":
    migrate_database()
