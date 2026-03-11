from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# الصفحة الرئيسية
def home(request):
    return render(request, 'home.html')


# تسجيل الدخول
def auth(request):
    page = 'login'

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username:
            username = username.lower()

        # ✅ التحقق من وجود المستخدم بطريقة أحسن
        try:
            user_exists = User.objects.filter(username=username).exists()
        except:
            user_exists = False

        if not user_exists:
            messages.error(request, 'User does not exist')
            return render(request, 'auth.html', {'page': page})  # ✅ استخدم render

        # محاولة تسجيل الدخول
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password is incorrect')
            return render(request, 'auth.html', {'page': page})  # ✅ استخدم render

    context = {'page': page}
    return render(request, 'auth.html', context)


# تسجيل الخروج
def logoutuser(request):
    logout(request)
    return redirect('home')


# إنشاء حساب
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
            messages.error(request, 'An error occurred during registration')
            return render(request, 'reg.html', {'form': form})  # ✅ أضف return هنا

    return render(request, 'reg.html', {'form': form})
