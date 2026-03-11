from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

# الصفحة الرئيسية (بعد تسجيل الدخول)
def home(request):
    return render(request, 'home.html')


# صفحة تسجيل الدخول
def auth(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
       
        # authenticate بتجيب المستخدم وتتأكد من كلمة السر
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
            return render(request, 'auth.html', {'page': page})

    context = {'page': page}
    return render(request, 'auth.html', context)


# صفحة تسجيل الخروج
def logoutuser(request):
    logout(request)
    return redirect('home')


# صفحة التسجيل (إنشاء حساب جديد)
def registerUser(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'حدث خطأ أثناء التسجيل')
    
    return render(request, 'reg.html', {'form': form})
