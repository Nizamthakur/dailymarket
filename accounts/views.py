from django.shortcuts import render, redirect
from products.models import PlacedOder, CompletedOder
from .forms import RegistrationForm, CustomUserEditForm, VendorRegistrationForm
from products.models import PlacedOder, CompletedOder,PlacedeOderItem
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import vendor_required
from django.db.models import Sum, F, DecimalField, Q
from Vendors.models import VendorStore
from django.db import models
from Vendors.models import WithdrawRequest
from products.forms import WithdrawRequestForm
@login_required
def create_withdraw_request(request):
    vendor = VendorStore.objects.get(user=request.user)

    if request.method == "POST":
        form = WithdrawRequestForm(request.POST)
        if form.is_valid():
            withdraw = form.save(commit=False)
            withdraw.vendor = vendor
            withdraw.save()
            return redirect("vendor_dashboard")  # dashboard এ redirect
    else:
        form = WithdrawRequestForm()

    return render(request, "wallet/withdraw_request_form.html", {"form": form})

# -------------------- User Registration --------------------
def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account created successfully!!!')
            return redirect('user_login')
    else:
        form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/user/registration.html', context)


# -------------------- Vendor Registration --------------------
def vendor_registration_view(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_role = '3'  # Vendor
            user.vendor_type = form.cleaned_data['vendor_type']  # Save dropdown selection
            user.is_vendor_approved = False  # admin approval required
            user.save()
            messages.success(request, "Your vendor account request has been submitted. Wait for admin approval.")
            return redirect('user_login')
    else:
        form = VendorRegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/vendor/vendor_registration.html', context)


# -------------------- Login --------------------
def login_view(request):
    if request.method == 'POST':
        login_form = AuthenticationForm(request, data=request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(username=email, password=password)
            if user is not None:
                # Vendor approval check
                if user.user_role == '3' and not user.is_vendor_approved:
                    messages.error(request, "Your vendor account is not approved yet. Please wait for admin approval.")
                    return redirect('user_login')

                login(request, user)
                return redirect('user_dashboard')  # role-based redirect
    else:
        login_form = AuthenticationForm()
    context = {
        'login_form': login_form
    }
    return render(request, 'accounts/user/login.html', context)

# -------------------- Vendor Dashboard ------------------
@login_required(login_url='user_login')

def vendor_dashboard(request):
    vendor = VendorStore.objects.get(user=request.user)

    # Vendor-এর shipped product-items
    sold_items = PlacedeOderItem.objects.filter(
        product__vendor_stores=vendor,
        placed_oder__status='Oder Shipped'
    )

    total_products_sold = sold_items.aggregate(total_qty=Sum('quantity'))['total_qty'] or 0

    # 80% revenue
    total_sales_80 = sold_items.aggregate(total_price=Sum(F('total_price') * 0.8))['total_price'] or 0

    # Approved withdraws deduct
    approved_withdraws = WithdrawRequest.objects.filter(
        vendor=vendor, status='approved'
    ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

    vendor_balance = float(total_sales_80 or 0) - float(approved_withdraws or 0)

    # Withdraw Requests
    withdraw_requests = WithdrawRequest.objects.filter(vendor=vendor).order_by('-created_at')

    # Number of orders
    orders_count = sold_items.values('placed_oder').distinct().count()

    context = {
        'vendor': vendor,
        'total_products_sold': total_products_sold,
        'vendor_balance': vendor_balance,
        'withdraw_requests': withdraw_requests,
        'orders_count': orders_count,
    }

    return render(request, 'accounts/vendor/vendor_dashboard.html', context)


# -------------------- User Dashboard --------------------
@login_required(login_url='user_login')
def user_dashboard(request):
    placed_orders = PlacedOder.objects.filter(user=request.user)
    completed_orders = CompletedOder.objects.filter(user=request.user)

    # Shipping address from the latest placed order
    shipping_address = placed_orders.first().shipping_address if placed_orders.exists() else None

    # Total number of products in placed orders (from related order_items)
    total_products_placed = placed_orders.aggregate(
        total=Sum('order_items__quantity')
    )['total'] or 0

    # Total number of products in completed orders (from related delivered_items)
    total_products_completed = completed_orders.aggregate(
        total=Sum('delivered_items__quantity')
    )['total'] or 0

    # 80% of total order amount (using sub_total_price)
    total_amount = placed_orders.aggregate(
        total=Sum('sub_total_price')
    )['total'] or 0
    total_amount_80_percent = total_amount * 0.8

    context = {
        'placed_oders_by_oder_id': placed_orders,
        'shipping_addesss': shipping_address,
        'completed_order': completed_orders,
        'total_products_placed': total_products_placed,
        'total_products_completed': total_products_completed,
        'total_amount_80_percent': total_amount_80_percent,
    }

    return render(request, 'accounts/user/user-dashboard.html', context)


# -------------------- Vendor Dashboard --------------------
@login_required(login_url='user_login')
def dashboard_redirect(request):
    if request.user.user_role == '3':  # Vendor
        return redirect('vendor_dashboard')
    else:  # Customer/User
        return redirect('user_dashboard')


# -------------------- Logout --------------------
@login_required(login_url='user_login')
def user_logout(request):
    logout(request)
    return redirect('home')


# -------------------- User Profile --------------------
@login_required(login_url='user_login')
def user_profile(request):
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('user_profile')
    else:
        form = CustomUserEditForm(instance=request.user)

    context = {
        "form": form
    }
    return render(request, 'accounts/user/user-profile.html', context)
