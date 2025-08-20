from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .cart import Cart
from store.models import Product, Order, OrderItem

# Add product to cart
def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product, quantity=1)
    return redirect('cart:view_cart')

# Remove product from cart
def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:view_cart')

# Clear the cart
def clear_cart(request):
    cart = Cart(request)
    cart.clear()
    return redirect('cart:view_cart')

# View cart items
def view_cart(request):
    cart = Cart(request)
    products = list(cart)
    total_price = cart.get_total_price()
    return render(request, 'cart/view_cart.html', {'cart_items': products, 'total_price': total_price})

# Checkout and place order
@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('store:home')  # Redirect if cart is empty

    if request.method == "POST":
        # Customer info
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        # Shipping info
        street_address = request.POST.get('street_address')
        apartment = request.POST.get('apartment')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        landmark = request.POST.get('landmark')
        address_type = request.POST.get('address_type')
        payment_method = request.POST.get('payment_method')

        shipping_address = f"{street_address}, {apartment or ''}, {city}, {state}, {pincode}, {landmark or ''} ({address_type})"

        total_price = cart.get_total_price()

        # Create order
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            shipping_address=shipping_address,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            payment_method=payment_method
        )

        # Add order items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )

        cart.clear()

        return render(request, 'cart/order_confirmation.html', {'order': order})

    return render(
        request,
        'cart/checkout.html',
        {
            'cart_items': list(cart),
            'total_price': cart.get_total_price()
        }
    )
