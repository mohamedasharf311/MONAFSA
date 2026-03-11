from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

# الصفحة الرئيسية
def home(request):
    return render(request, 'home.html')

# صفحة تسجيل الدخول
def auth(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').lower().strip()
        password = request.POST.get('password', '')
        
        # التحقق من أن الحقول مش فاضية
        if not username or not password:
            messages.error(request, 'من فضلك أدخل اسم المستخدم وكلمة المرور')
            return render(request, 'auth.html')
        
        # محاولة تسجيل الدخول
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
            return render(request, 'auth.html')
    
    # لو الطلب GET
    return render(request, 'auth.html')

# صفحة تسجيل الخروج
def logoutuser(request):
    logout(request)
    return redirect('home')

# صفحة التسجيل
def registerUser(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').lower().strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # التحقق من الحقول
        if not username or not email or not password:
            messages.error(request, 'من فضلك أدخل جميع الحقول')
            return render(request, 'reg.html')
        
        if password != confirm_password:
            messages.error(request, 'كلمة المرور غير متطابقة')
            return render(request, 'reg.html')
        
        # التحقق من وجود المستخدم
        if User.objects.filter(username=username).exists():
            messages.error(request, 'اسم المستخدم موجود بالفعل')
            return render(request, 'reg.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'البريد الإلكتروني مستخدم بالفعل')
            return render(request, 'reg.html')
        
        # إنشاء المستخدم الجديد
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.save()
            
            # تسجيل الدخول مباشرة بعد التسجيل
            login(request, user)
            return redirect('home')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
            return render(request, 'reg.html')
    
    # لو الطلب GET
    return render(request, 'reg.html')
