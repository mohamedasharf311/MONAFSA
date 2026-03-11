from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import traceback
import sys

# الصفحة الرئيسية
def home(request):
    return render(request, 'home.html')


# تسجيل الدخول - نسخة مبسطة جداً
def auth(request):
    print("=" * 50, file=sys.stderr)
    print("AUTH VIEW CALLED", file=sys.stderr)
    print("Method:", request.method, file=sys.stderr)
    
    if request.method == 'POST':
        try:
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            
            print(f"Username: {username}", file=sys.stderr)
            print(f"Password length: {len(password) if password else 0}", file=sys.stderr)
            
            # محاولة تسجيل الدخول مباشرة
            user = authenticate(request, username=username, password=password)
            print(f"Authenticate result: {user}", file=sys.stderr)
            
            if user is not None:
                login(request, user)
                print("Login successful", file=sys.stderr)
                return redirect('home')
            else:
                print("Authentication failed", file=sys.stderr)
                messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
                return render(request, 'auth.html')
                
        except Exception as e:
            print(f"ERROR: {str(e)}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            messages.error(request, f'خطأ: {str(e)}')
            return render(request, 'auth.html')
    
    print("GET request", file=sys.stderr)
    return render(request, 'auth.html')


# تسجيل الخروج
def logoutuser(request):
    logout(request)
    return redirect('home')


# إنشاء حساب
def registerUser(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username', '').lower()
            email = request.POST.get('email', '')
            password = request.POST.get('password', '')
            confirm = request.POST.get('confirm_password', '')
            
            if password != confirm:
                messages.error(request, 'كلمة المرور غير متطابقة')
                return render(request, 'reg.html')
            
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            login(request, user)
            return redirect('home')
            
        except Exception as e:
            print(f"Register error: {str(e)}", file=sys.stderr)
            messages.error(request, f'خطأ في التسجيل: {str(e)}')
            return render(request, 'reg.html')
    
    return render(request, 'reg.html')
