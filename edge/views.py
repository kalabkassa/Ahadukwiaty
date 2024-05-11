from django.shortcuts import render, get_object_or_404
from .models import Flower

from django.shortcuts import HttpResponse
from django.views.decorators.http import require_POST
import json
from django.http import JsonResponse
from django.shortcuts import redirect
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import authenticate, login

from django.contrib.auth.decorators import login_required
from .models import CartItem

import paypalrestsdk


# Initialize PayPal SDK
# paypalrestsdk.configure({
#     "mode": "sandbox",  # Use 'sandbox' for testing and 'live' for production
#     "client_id": 'AV5W7joFIbxEhZI-7N0s7GdP7Hi9uTa4vGc-Z1ygLBQCW0nbQifUQvRKVYJFS-pe46yHeHBC-oNT-clE',
#     "client_secret": 'EEa8JJO4UpQfkllJctcEOaool1Lcl5UgVvZigAHhdQLN4MfcNATMSgj3PNscZIwjVfKKkE01ZVjgDoE1'
# })

# Create your views here.
def index(request):
    flowers = Flower.objects.all()
    return render(request, 'edge/index.html', {'flowers': flowers})

def flowers(request):
    flowers = Flower.objects.all()
    return render(request, 'edge/Flowers.html', {'flowers': flowers})

def aboutus(request):
    return render(request, 'edge/aboutus.html')

def contact(request):
    return render(request, 'edge/contactus.html')

def delivery(request):
    return render(request, "edge/Delivery.html")

def wishlist(request):
    return render(request, 'edge/wishlist.html')

def products(request, id):
    flower = Flower.objects.get(pk=id)
    return render(request, "edge/products.html", {'flower':  flower})

def add_to_cart(request):
    if request.method == 'POST':
        flower_id = request.POST.get('flower_id')
        flower_size = request.POST.get('flower_size')
        flower_num = request.POST.get('flower_num')

        cart = request.session.get('cart', [])

        cart.append(flower_id + ',' + flower_size + ',' + flower_num)

        request.session['cart'] = cart
        updatedb_cart_item(request)
        return HttpResponse(json.dumps({'success': True}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': 'Method not allowed'}), status=405, content_type="application/json")

def remove_from_cart(request):
    if request.method == 'POST':
        # Assuming the product ID is sent in the request body
        data = json.loads(request.body)
        flower_id = data.get('flower_id')
        flower_size = data.get('flower_size')
        flower_num = data.get('flower_num')
        flower = (str(flower_id) + ',' + flower_size + ',' + flower_num)

        # Remove the product from the session
        if 'cart' in request.session:
            cart = request.session['cart']
            if flower in cart:
                cart.remove(flower)
                get_object_or_404(CartItem, user=request.user, flower_id=flower_id).delete()
                request.session['cart'] = cart
                return JsonResponse({'message': 'Product removed from cart'}, status=200)
            else:
                return JsonResponse({'error': 'Product not found in cart'}, status=400)
        else:
            return JsonResponse({'error': 'Cart not found in session'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

def update_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        flower_id = data.get('flower_id')
        flower_size = data.get('flower_size')
        flower_num = data.get('flower_num')
        flower = (str(flower_id) + ',' + flower_size + ',' + flower_num)

        if 'cart' in request.session:
            cart = request.session['cart']
            cart[flower]['size'] = flower_size
        updatedb_cart_item(request)

def get_cart(request):
    updatedb_cart(request)
    cart = request.session.get('cart', [])
    # You may want to retrieve the actual product objects based on the product IDs in the cart
    # For simplicity, I'll just return the product IDs as JSON
    cart_html = ''
    cart_total_price = 0
    if cart:
        for flower in cart:
            cart_html += '<div class="checkoutlist">'
            flower = flower.split(',')
            flower_id = flower[0]
            flower_size = flower[1]
            flower_num = flower[2]
            flower = Flower.objects.get(pk=flower_id)
            cart_html += '<div class = "checkoutimage"><img src="/edge/media/{0}" alt="" /></div>'.format(flower.image)
            cart_html += '<div class="checkdetail"> <div class="checkfirst">'
            cart_html += '<h2>{0}</h2>'.format(flower.name)
            cart_html += '<svg  onclick="removeCart({0},\'{1}\')" fill="#B7B0B5" height="clamp(1rem, 1.5vw, 2rem)" viewBox="0 0 32 32" version="1.1" xmlns="http://www.w3.org/2000/svg"> <path d="M16 0c-8.836 0-16 7.163-16 16s7.163 16 16 16c8.837 0 16-7.163 16-16s-7.163-16-16-16zM16 30.032c-7.72 0-14-6.312-14-14.032s6.28-14 14-14 14 6.28 14 14-6.28 14.032-14 14.032zM21.657 10.344c-0.39-0.39-1.023-0.39-1.414 0l-4.242 4.242-4.242-4.242c-0.39-0.39-1.024-0.39-1.415 0s-0.39 1.024 0 1.414l4.242 4.242-4.242 4.242c-0.39 0.39-0.39 1.024 0 1.414s1.024 0.39 1.415 0l4.242-4.242 4.242 4.242c0.39 0.39 1.023 0.39 1.414 0s0.39-1.024 0-1.414l-4.242-4.242 4.242-4.242c0.391-0.391 0.391-1.024 0-1.414z"></path> </svg>'.format(flower_id, flower_size)
            cart_html += '</div> <div class="checksecond"><h2>Size:</h2>'
            cart_html += '<h2>{0}</h2></div><div class="row2"><button class="minus" id="{1}" onclick="sub(this.id, \'{0}\')">&#8210;</button><input id="input_{1}" type="text" value={2} /><button class="plus" id="{1}" onclick="add(this.id, \'{0}\')">&plus;</button></div>'.format(flower_size, flower_id, flower_num)
            cart_html += '</div></div>'
            if flower_size == 'S':
                flower_price = flower.price_s
            elif flower_size == 'M':
                flower_price = flower.price_m
            elif flower_size == 'L':
                flower_price = flower.price_l
            elif flower_size == 'XL':
                flower_price = flower.price_xl
            elif flower_size == 'XXL':
                flower_price = flower.price_xxl
            cart_total_price += flower_price
    return JsonResponse({'html': cart_html, 'total_price': cart_total_price})

def checkout(request):
    cart = request.session.get('cart', [])
    # You may want to retrieve the actual product objects based on the product IDs in the cart
    # For simplicity, I'll just return the product IDs as JSON
    flowers = []
    flower_sizes = []
    flower_price = []
    flower_num = []
    if cart:
        for flower in cart:
            flower = flower.split(',')
            flower_id = flower[0]
            flower_size = flower[1]
            flower_num.append(flower[2])
            flower_sizes.append(flower_size)
            flower = Flower.objects.get(pk=flower_id)
            flowers.append(flower)
            if flower_size == 'S':
                flower_price.append(flower.price_s)
            elif flower_size == 'M':
                flower_price.append(flower.price_m)
            elif flower_size == 'L':
                flower_price.append(flower.price_l)
            elif flower_size == 'XL':
                flower_price.append(flower.price_xl)
            elif flower_size == 'XXL':
                flower_price.append(flower.price_xxl)
        total_price = 0
        for price in flower_price:
            total_price += price
        return render(request, "edge/checkout.html", {'client_id': 'AV5W7joFIbxEhZI-7N0s7GdP7Hi9uTa4vGc-Z1ygLBQCW0nbQifUQvRKVYJFS-pe46yHeHBC-oNT-clE','flowers': flowers, 'flower_sizes': flower_sizes, 'flower_num': flower_num, 'flower_price': flower_price,'total_price': total_price})
    return redirect("edge/Flowers.html")

def create_payment(request):
    # Calculate the total amount on the server-side
    total_amount = calc_total_price(request)  # Example amount
    
    # # Create Payment object
    # payment = paypalrestsdk.Payment({
    #     "intent": "sale",
    #     "payer": {
    #         "payment_method": "paypal"
    #     },
    #     "redirect_urls": {
    #         "return_url": "http://localhost:8000/payment/execute/",
    #         "cancel_url": "http://localhost:8000/payment/cancel/"
    #     },
    #     "transactions": [{
    #         "amount": {
    #             "total": str(total_amount),
    #             "currency": "USD"
    #         },
    #         "description": "Test Transaction"
    #     }]
    # })

    # # Create payment
    # if payment.create():
    #     return JsonResponse({"payment_id": payment.id, "total_amount": total_amount})
    # else:
    #     return JsonResponse({"error": payment.error})
    
# utility functions
def calc_total_price(request):
    cart = request.session.get('cart', [])
    flower_price = []

    if cart:
        for flower in cart:
            flower = flower.split(',')
            flower_id = flower[0]
            flower_size = flower[1]
            flower = Flower.objects.get(pk=flower_id)
            if flower_size == 'S':
                flower_price.append(flower.price_s)
            elif flower_size == 'M':
                flower_price.append(flower.price_m)
            elif flower_size == 'L':
                flower_price.append(flower.price_l)
            elif flower_size == 'XL':
                flower_price.append(flower.price_xl)
            elif flower_size == 'XXL':
                flower_price.append(flower.price_xxl)
        total_price = 0
        for price in flower_price:
            total_price += price
    return total_price

@login_required
def updatedb_cart_item(request):
    if request.session.get('cart'):
        cart = request.session.get('cart')
        # Update or create cart items in the database
        
        for flower in cart:
            flower = flower.split(',')
            flower_id = flower[0]
            flower_size = flower[1]
            flower_num = flower[2]
            # Check if the item already exists in the database
            cart_item, created = CartItem.objects.get_or_create(user=request.user, flower_id=flower_id, flower_num=flower_num, flower_size=flower_size)
            # Update the quantity if the item exists
            if not created:
                cart_item.flower_size = flower_size
                cart_item.flower_num = flower_num
                cart_item.save()

        del request.session['cart']

    cart_items = CartItem.objects.filter(user=request.user)
    cart = request.session.get('cart', [])

    for flower_item in cart_items:
        cart.append(str(flower_item.flower_id) + ',' + flower_item.flower_size + ',' + str(flower_item.flower_num))
    print(cart)
    request.session['cart'] = cart

@login_required
def updatedb_cart(request):
    del request.session['cart']
    cart_items = CartItem.objects.filter(user=request.user)
    print(cart_items)
    cart = request.session.get('cart', [])

    for flower_item in cart_items:
        cart.append(str(flower_item.flower_id) + ',' + flower_item.flower_size + ',' + str(flower_item.flower_num))
    request.session['cart'] = cart
    return JsonResponse({'message': 'db cart updated'}, status=200)

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'edge/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to the home page or a specific page
                updatedb_cart_item(request)
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'edge/login.html', {'form': form})
