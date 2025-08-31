from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Avg
from django.db.models import F
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import (
    Product, Industry, Cart, CustomerAddress,
    PlacedOder, PlacedeOderItem, CuponCodeGenaration,
    ProductStarRatingAndReview, Categories,HelpVideo, Complain,ResellProduct
)
from .forms import CustomerAddressForm,OrderComplainForm
from accounts.models import CustomUser
import json


# --------------------- PRODUCT VIEWS --------------------- #
def product_details(request, slug):
    product = get_object_or_404(Product, slug=slug)
    industry = Industry.objects.all()

    # Get all reviews for this product
    product_reviews = ProductStarRatingAndReview.objects.filter(product=product)
    Product.objects.filter(id=product.id).update(views=F('views') + 1)
    product.refresh_from_db()
    # Calculate average stars (rounded)
    avg_rating = product_reviews.aggregate(avg_stars=Avg('stars'))['avg_stars'] or 0
    avg_rating = round(avg_rating)

    context = {
        "product": product,
        "industry": industry,
        "product_reviews": product_reviews,
        "avg_rating": avg_rating,
    }
    return render(request, "products/product-details.html", context)




def bottom_area(request):
    # Top 5 featured products
    featured_products = Product.objects.filter(is_featured=True).order_by('-created_at')[:5]
    industry = Industry.objects.all()

    for product in featured_products:
        # Average rating
        avg_stars = product.productstarratingandreview_set.aggregate(avg=Avg('stars'))['avg'] or 0
        product.avg_rating = round(avg_stars)

        # Discounted percent
        if product.regular_price > 0 and product.discounted_price < product.regular_price:
            product.discounted_parcent = int(100 - (product.discounted_price / product.regular_price * 100))
        else:
            product.discounted_parcent = 0

        # Sold count & percentage
        sold_count = sum(item.quantity for item in product.orderitem_set.all()) if hasattr(product, 'orderitem_set') else 0
        product.sold_count = sold_count
        product.sold_percentage = int((sold_count / product.stoc) * 100) if product.stoc > 0 else 0

    context = {
        'featured_products': featured_products,
        'industry': industry
    }

    return render(request, "home/bottom-area.html", context)




# --------------------- ALL PRODUCTS --------------------- #
def all_products(request):
    products = Product.objects.all()
    industry = Industry.objects.all()

    # Filter by category (from banner) or featured
    category_slug = request.GET.get('category')  # slug নাও
    featured = request.GET.get('featured')

    if category_slug:
        try:
            category = Categories.objects.get(slug=category_slug)  # slug দিয়ে category object খুঁজো
            products = products.filter(categories=category)
            page_title = category.name
        except Categories.DoesNotExist:
            products = Product.objects.none()
            page_title = "No Products"
    elif featured:
        # Filter only featured products
        products = products.filter(is_featured=True)
        page_title = "Featured Products"
    else:
        page_title = "All Products"

    # Add extra info for template
    for product in products:
        avg_stars = product.productstarratingandreview_set.aggregate(avg=Avg('stars'))['avg'] or 0
        product.avg_rating = round(avg_stars)

        # Discount calculation
        if product.regular_price > 0 and product.discounted_price < product.regular_price:
            product.discounted_percent = int(100 - (product.discounted_price / product.regular_price * 100))
        else:
            product.discounted_percent = 0

        # Lines for short description
        if product.details_description:
            product.lines = product.details_description.splitlines()[:4]
        else:
            product.lines = []

    context = {
        'products': products,
        'industry': industry,
        'page_title': page_title,
    }

    return render(request, 'products/all-products.html', context)

# --------------------- CART VIEWS --------------------- #
@login_required(login_url="user_login")
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    cart_obj, created = Cart.objects.get_or_create(user=request.user, product=product)
    return redirect('show_cart')


@login_required(login_url="user_login")
def show_cart(request):
    carts = Cart.objects.filter(user=request.user)
    industry = Industry.objects.all()
    sub_total = Cart.subtotal_product_price(user=request.user) if carts else 0.00
    context = {
        "carts": carts,
        "sub_total": format(sub_total, '.2f'),
        'industry': industry
    }
    return render(request, "products/cart.html", context)


@login_required(login_url="user_login")
@csrf_exempt
def increase_cart(request):
    if request.method == "POST":
        data = json.loads(request.body)
        id = int(data['id'])
        values = int(data['values'])
        product = get_object_or_404(Cart, id=id, user=request.user)

        if values == 1 and product.quantity < 50:
            product.quantity += 1
            product.save()
        elif values == 2 and product.quantity > 1:
            product.quantity -= 1
            product.save()
        elif values == 0:
            product.delete()
            return JsonResponse({"status": "deleted"})

        sub_total = Cart.subtotal_product_price(user=request.user)
        return JsonResponse({
            "product_quantity": product.quantity,
            "total_product_price": product.total_product_price,
            'sub_total': sub_total
        })



# --------------------- CHECKOUT VIEWS --------------------- #


@login_required(login_url="user_login")
def check_out(request):
    user_cart = Cart.objects.filter(user=request.user)
    all_shipping_address = CustomerAddress.objects.filter(user=request.user)

    if not user_cart.exists():
        messages.info(request, 'You have no product in your Cart')
        return redirect('home')

    first_cart_item = user_cart.first()
    selected_shipping_address = first_cart_item.shipping_address or (all_shipping_address.last() if all_shipping_address.exists() else None)

    shipping_charge = 90  # Fixed shipping

    if request.method == 'POST':
        # ---------- Handle Address ----------
        selected_address_id = request.POST.get('selected_address_id')
        if selected_address_id:
            selected_shipping_address = get_object_or_404(CustomerAddress, id=selected_address_id)
            first_cart_item.shipping_address = selected_shipping_address
            first_cart_item.save()

        # Ensure shipping address exists
        if not selected_shipping_address:
            messages.error(request, "আপনার জন্য একটি Shipping Address নির্বাচন করতে হবে বা নতুন Address যুক্ত করুন।")
            return redirect('check_out')

        # ---------- Handle Payment ----------
        payment_method = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id') if payment_method in ['bkash', 'nagad'] else None

        sub_total = Cart.subtotal_product_price(user=request.user)
        order_total = sub_total + shipping_charge

        # Validate payment input for Bkash/Nagad
        if payment_method in ['bkash', 'nagad'] and not transaction_id:
            messages.error(request, "Bkash/Nagad এর জন্য Transaction ID দিতে হবে।")
            return redirect('check_out')

        # ---------- Save Order ----------
        order = PlacedOder.objects.create(
            user=request.user,
            payment_method=payment_method,
            transaction_id=transaction_id,
            shipping_address=selected_shipping_address,
            sub_total_price=sub_total,
            paid=True if payment_method in ['bkash', 'nagad'] else False
        )

        # ---------- Save Ordered Items ----------
        for item in user_cart:
            PlacedeOderItem.objects.create(
                placed_oder=order,
                product=item.product,
                quantity=item.quantity,
                total_price=item.total_product_price
            )

        # ---------- Clear Cart ----------
        user_cart.delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect("placed_oder")  # Or a custom success page

    # ---------- GET Request ----------
    remove_cupon = request.GET.get('remove_cupon')
    if remove_cupon:
        for item in user_cart:
            item.cupon_applaied = False
            item.cupon_code = None
            item.save()

    cupon = user_cart[0].cupon_applaied if user_cart and user_cart[0].cupon_applaied else False
    sub_total = Cart.subtotal_product_price(user=request.user)
    order_total = sub_total + shipping_charge
    address_form = CustomerAddressForm()
    industry = Industry.objects.all()

    context = {
        'address_form': address_form,
        'cupon': cupon,
        'carts': user_cart,
        'sub_total': sub_total,
        'shipping_charge': shipping_charge,
        'order_total': order_total,
        'industry': industry,
        'all_shipping_address': all_shipping_address,
        'selected_shipping_address': selected_shipping_address
    }
    return render(request, 'products/checkout.html', context)


@login_required(login_url="user_login")
def add_address(request):
    if request.method == "POST":
        form = CustomerAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "New address added successfully!")
            return redirect('check_out')
    else:
        form = CustomerAddressForm()
    return render(request, 'products/add_address.html', {'form': form})




@login_required(login_url="user_login")
def placed_oder(request):
    user_cart = Cart.objects.filter(user=request.user)
    if not user_cart.exists():
        messages.info(request, "No product in cart to place order")
        return redirect("home")

    sub_total_price = Cart.subtotal_product_price(request.user)
    placed_order = PlacedOder.objects.create(
        user=request.user,
        shipping_address=user_cart.first().shipping_address,
        sub_total_price=sub_total_price,
        paid=True
    )

    for item in user_cart:
        PlacedeOderItem.objects.create(
            placed_oder=placed_order,
            product=item.product,
            quantity=item.quantity,
            total_price=item.total_product_price
        )
        item.delete()

    messages.success(request, 'Order Placed Successfully')
    return redirect('user_dashboard')


@login_required(login_url="user_login")
def cupon_apply(request):
    if request.method == 'POST':
        cupon_code = request.POST.get('cupon_code')
        cupon_obj = CuponCodeGenaration.objects.filter(cupon_code=cupon_code).first()
        if cupon_obj:
            user_carts = Cart.objects.filter(user=request.user)
            for item in user_carts:
                item.cupon_code = cupon_obj
                item.cupon_applaied = True
                item.save()
    return redirect('check_out')


@login_required(login_url="user_login")
def add_product_review_and_rating(request):
    if not request.user.is_authenticated or request.user.user_role != '1':
        messages.info(request, f"{request.user.first_name} is not a customer!")
        return redirect('/')

    if request.method == 'POST':
        data = json.loads(request.body)
        product_obj = get_object_or_404(Product, id=int(data.get('product_id')))
        stars = int(data.get('stars'))
        review_messages = data.get('review_messages')

        ProductStarRatingAndReview.objects.create(
            product=product_obj,
            user=request.user,
            stars=stars,
            review_message=review_messages
        )
        return JsonResponse({"status": 200})


@login_required(login_url="user_login")
def save_shipping_address(request):
    if request.method == 'POST':
        new_address_form = CustomerAddressForm(data=request.POST)
        if new_address_form.is_valid():
            new_address = new_address_form.save(commit=False)
            new_address.user = request.user
            new_address.save()

            user_cart = Cart.objects.filter(user=request.user).first()
            if user_cart:
                user_cart.shipping_address = new_address
                user_cart.save()
    return redirect('check_out')

def search_products(request):
    query = request.GET.get('q', '')  # 'q' is the name of the input
    if query:
        products = Product.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    else:
        products = Product.objects.none()  # No query, return empty

    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'products/search_results.html', context)

def footer_help(request):
    # Fetch videos dynamically
    how_to_use_video = get_object_or_404(HelpVideo, slug='how-to-use-account')
    placing_order_video = get_object_or_404(HelpVideo, slug='placing-order')

    context = {
        'how_to_use_video_url': how_to_use_video.video_file.url,
        'placing_order_video_url': placing_order_video.video_file.url,
    }
    return render(request, 'baseFiles/base.html', context)

def payment_methods(request):
    return render(request, 'products/payment_methods.html')


@login_required
def submit_complain(request):
    if request.method == "POST":
        form = OrderComplainForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your complain has been submitted successfully.")
        else:
            messages.error(request, "There was an error submitting your complain.")
    return redirect("home")

def resell_products(request):
    products = ResellProduct.objects.all().order_by('-created_at')
    return render(request, "products/resell_products.html", {"products": products})

