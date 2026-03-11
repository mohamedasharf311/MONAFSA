from django.shortcuts import render , redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import authenticate , login , logout
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
def home(request):
    return render(request, 'home.html')


def auth(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
       
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'user dose not exist')  
         
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request , user)
            return redirect('home')

    context = {'page' : page}
    return render(request, 'auth.html' , context)

def logoutuser(request):
    logout(request)
    return redirect('home')


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
            messages.error(request , 'An error occurred during registration')
    return render(request , 'reg.html', {'form':form})