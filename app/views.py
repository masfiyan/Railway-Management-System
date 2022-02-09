from django.shortcuts import render, redirect
from django.views import View
from app.models import CustomUser
from django.http import HttpResponse
from django.contrib import messages


# Create your views here.


class Home(View):
    def get(self, request):
        return render(request, 'home.html')


class Login(View):
    def get(self, request):
        return render(request, 'login.html')


# class Signup(View):
#     def get(self, request):
#         return render(request, 'signup.html')

def signup(request):
    if request.method=="POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']        
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.warning(request,"Password didn't matched")
            return redirect('signup')
      
        elif username == '':
            messages.warning(request,"Please enter a username")
            return redirect('signup')

        elif first_name == '':
            messages.warning(request,"Please enter first name")
            return redirect('signup')

        elif last_name == '':
            messages.warning(request,"Please enter last name")
            return redirect('signup')

        elif email == '':
            messages.warning(request,"Please enter email address")
            return redirect('signup')

        elif phone == '':
            messages.warning(request,"Please enter phone number")
            return redirect('signup')

        elif password1 == '':
            messages.warning(request,"Please enter password")
            return redirect('signup')

        elif password2 == '':
            messages.warning(request,"Please enter confirm password")
            return redirect('signup')
        
        try:
            if CustomUser.objects.all().get(username=username):
                messages.warning(request,"username not Available")
                return redirect('signup')

        except:
            pass
            

        new_user = CustomUser.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, phone=phone, password=password1)
        new_user.is_superuser=False
        new_user.is_staff=False
            
        new_user.save()
        messages.success(request,"Registration Successfull")
        return redirect("login")
    return render(request, 'signup.html')