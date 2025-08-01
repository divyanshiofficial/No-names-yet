from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .models import UserProfile
from django.urls import reverse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
import pandas as pd
import os

from .models import Product, CartItem, UserProfile
from .forms import RegisterForm, LoginForm


def upload_csv(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'csvs'))
        filename = fs.save('latest.csv', csv_file)  # overwrite latest.csv each time
        return redirect('upload_success')
    return render(request, 'store/upload_csv.html')


def upload_success(request):
    return render(request, 'store/upload_success.html')


def home(request):
    categories = ['tops', 'bottoms', 'dresses', 'loungewear', 'outerwear']
    return render(request, 'store/home.html', {'categories': categories})


@login_required
def catalog(request):
    selected_category = request.GET.get('category')
    if selected_category:
        items = Product.objects.filter(category__iexact=selected_category)
    else:
        items = Product.objects.all()

    cart_items = CartItem.objects.filter(user=request.user)
    cart_dict = {str(item.product.id): item.quantity for item in cart_items}

    categories = ['Tops', 'Bottoms', 'Dresses', 'Loungewear', 'Outerwear']
    return render(request, 'store/catalog.html', {
        'items': items,
        'categories': categories,
        'selected_category': selected_category,
        'cart_quantities': cart_dict
    })


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'store/admin_login.html', {'error': 'Invalid credentials or not an admin'})

    return render(request, 'store/admin_login.html')


def admin_dashboard(request):
    if request.user.userprofile.role != 'admin':
        return redirect('customer_dashboard')  # or show a 403 page
    return render(request, 'store/admin_dashboard.html')
    


def customer_dashboard(request):
    return render(request, 'store/customer_dashboard.html')


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')


@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_total() for item in cart_items)
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})


@login_required
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        CartItem.objects.filter(id=item_id, user=request.user).delete()
    return redirect('cart')


@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_total() for item in cart_items)

    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total': total,
    })


@login_required
def payment_success(request):
    if request.method == 'POST':
        selected_method = request.POST.get('payment_method')
        address = request.POST.get('address')
        total = 0
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            total += item.get_total()

        cart_items.delete()

        return render(request, 'store/payment_success.html', {
            'method': selected_method,
            'total': total,
            'address': address
        })


def dashboard(request):
    csv_path = os.path.join(settings.MEDIA_ROOT, 'csvs', 'latest.csv')
    data = None
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        data = df.to_dict(orient='records')
    return render(request, 'store/dashboard.html', {'data': data})


# ✅ CUSTOMER AUTHENTICATION VIEWS BELOW

def register_customer(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(request, 'store/register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'store/register.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, role='customer')

        login(request, user)
        return redirect('customer_dashboard')

    return render(request, 'store/register.html')

def login_customer(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_superuser or user.userprofile.role == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('customer_dashboard')
        else:
            return render(request, 'store/login.html', {'error': 'Invalid credentials'})
    return render(request, 'store/login.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # After registration, go to login
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin_dashboard')
                else:
                    return redirect('customer_dashboard')
    else:
        form = LoginForm()
    return render(request, 'store/login.html', {'form': form})


def logout_customer(request):
    logout(request)
    return redirect('login')
