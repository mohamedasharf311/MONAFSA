from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

def home(request):
    return render(request, 'home.html')

def auth(request):
    print("========== VIEW AUTH IS CALLED ==========")  # هذا سيظهر في سجلات Vercel
    
    if request.method == 'POST':
        print(f"POST data: {request.POST}")  # طباعة البيانات المرسلة
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"Username: {username}, Password: {password}")
        
        try:
            user = authenticate(request, username=username, password=password)
            print(f"Authenticate result: {user}")
            
            if user is not None:
                login(request, user)
                print("Login successful, redirecting to home")
                return redirect('home')
            else:
                print("Authentication failed")
                messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
                return render(request, 'auth.html')
        except Exception as e:
            print(f"EXCEPTION: {str(e)}")
            messages.error(request, f'خطأ: {str(e)}')
            return render(request, 'auth.html')
    
    return render(request, 'auth.html')

def logoutuser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'اسم المستخدم موجود')
                return render(request, 'reg.html')
            
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            login(request, user)
            return redirect('home')
        except Exception as e:
            messages.error(request, f'خطأ: {str(e)}')
            return render(request, 'reg.html')
    
    return render(request, 'reg.html')
