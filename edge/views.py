from django.shortcuts import render
from .models import Flower

from django.shortcuts import HttpResponse
from django.views.decorators.http import require_POST
import json
from django.http import JsonResponse


# Create your views here.
def index(request):
    return render(request, 'edge/index.html')

def flowers(request):
    flowers = Flower.objects.all()
    for flower in flowers:
        print(flower.image)
    return render(request, 'edge/Flowers.html', {'flowers': flowers})

def aboutus(request):
    return render(request, 'edge/aboutus.html')

def contact(request):
    return render(request, 'edge/contactus.html')

def delivery(request):
    return render(request, "edge/Delivery.html")

def wishlist(request):
    return render(request, 'edge/wishlist.html')

def products(request):
    return render(request, "edge/products.html")

def add_to_cart(request):
    if request.method == 'POST':
        flower_id = request.POST.get('flower_id')
        flower_size = request.POST.get('flower_size')
        print(flower_size)
        cart = request.session.get('cart', [])

        cart.append(flower_id + ',' + flower_size)

        request.session['cart'] = cart
        return HttpResponse(json.dumps({'success': True}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': 'Method not allowed'}), status=405, content_type="application/json")

def remove_from_cart(request):
    if request.method == 'POST':
        # Assuming the product ID is sent in the request body
        data = json.loads(request.body)
        flower_id = data.get('flower_id')
        flower_size = data.get('flower_size')
        flower = (str(flower_id) + ',' + flower_size)

        # Remove the product from the session
        if 'cart' in request.session:
            cart = request.session['cart']
            if flower in cart:
                cart.remove(flower)
                request.session['cart'] = cart
                print(cart)
                return JsonResponse({'message': 'Product removed from cart'}, status=200)
            else:
                return JsonResponse({'error': 'Product not found in cart'}, status=400)
        else:
            return JsonResponse({'error': 'Cart not found in session'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

def get_cart(request):
    cart = request.session.get('cart', [])
    # You may want to retrieve the actual product objects based on the product IDs in the cart
    # For simplicity, I'll just return the product IDs as JSON
    print(cart)
    cart_html = ''
    if cart:
        for flower in cart:
            cart_html += '<div class="checkoutlist">'
            flower = flower.split(',')
            flower_id = flower[0]
            flower_size = flower[1]
            flower = Flower.objects.get(pk=flower_id)
            cart_html += '<img src="/edge/media/{0}" alt="" />'.format(flower.image)
            cart_html += '<div class="checkdetail"> <div class="checkfirst">'
            cart_html += '<h2>{0}</h2>'.format(flower.name)
            cart_html += '<svg  onclick="removeCart({0},\'{1}\')" fill="#B7B0B5" height="1.5vw" viewBox="0 0 32 32" version="1.1" xmlns="http://www.w3.org/2000/svg"> <path d="M16 0c-8.836 0-16 7.163-16 16s7.163 16 16 16c8.837 0 16-7.163 16-16s-7.163-16-16-16zM16 30.032c-7.72 0-14-6.312-14-14.032s6.28-14 14-14 14 6.28 14 14-6.28 14.032-14 14.032zM21.657 10.344c-0.39-0.39-1.023-0.39-1.414 0l-4.242 4.242-4.242-4.242c-0.39-0.39-1.024-0.39-1.415 0s-0.39 1.024 0 1.414l4.242 4.242-4.242 4.242c-0.39 0.39-0.39 1.024 0 1.414s1.024 0.39 1.415 0l4.242-4.242 4.242 4.242c0.39 0.39 1.023 0.39 1.414 0s0.39-1.024 0-1.414l-4.242-4.242 4.242-4.242c0.391-0.391 0.391-1.024 0-1.414z"></path> </svg>'.format(flower_id, flower_size)
            cart_html += '</div> <div class="checksecond"><h2>Size:</h2>'
            cart_html += '<h2>{0}</h2></div><div class="row2"><button class="minus">&#8210;</button><input type="text" placeholder="1" /><button class="plus">&plus;</button></div>'.format(flower_size)
            cart_html += '</div></div>'
    return JsonResponse({'html': cart_html})

def checkout(request):
    return render(request, "edge/checkout.html")