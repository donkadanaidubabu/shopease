from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from rest_framework import generics, viewsets
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import string

from .models import Product, Category, Order, OrderItem
from .serializers import ProductSerializer, CategorySerializer
from cart.models import Cart, CartItem


# ------------------- Enhanced Chatbot -------------------
def chatbot_view(request):
    return render(request, "store/chatbot.html")


def chatbot_test_view(request):
    return render(request, "store/chatbot_test.html")


@csrf_exempt
def chatbot_message(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            # Normalize: lowercase, strip spaces, remove punctuation
            user_message_clean = user_message.lower().strip()
            user_message_clean = user_message_clean.translate(str.maketrans('', '', string.punctuation))

            # Handle guest or authenticated users
            user = request.user if request.user.is_authenticated else None
            cart, _ = Cart.objects.get_or_create(user=user)

            response = "I didn't fully understand that. Can you rephrase?"

            # --- Enhanced Greetings ---
            greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
            if any(greet in user_message_clean for greet in greetings):
                if user and user.is_authenticated:
                    response = f"Hello {user.first_name or user.username}! 👋 How can I help you with your shopping today?"
                else:
                    response = "Hello! 👋 Welcome to ShopEase! How can I help you today?"

            # --- Product Search ---
            elif "search" in user_message_clean or "find" in user_message_clean or "show me" in user_message_clean:
                search_terms = user_message_clean.replace("search", "").replace("find", "").replace("show me",
                                                                                                    "").strip()
                products = Product.objects.filter(
                    Q(name__icontains=search_terms) |
                    Q(description__icontains=search_terms) |
                    Q(category__name__icontains=search_terms)
                )[:5]

                if products:
                    response = f"🔍 Found {products.count()} products:\n"
                    for product in products:
                        response += f"• {product.name} - ${product.price}\n"
                    response += "\nWould you like to add any of these to your cart?"
                else:
                    response = "❌ Sorry, I couldn't find any products matching your search."

            # --- Categories ---
            elif "categories" in user_message_clean or "what do you sell" in user_message_clean:
                categories = Category.objects.all()
                if categories:
                    response = "📂 We have these categories:\n"
                    for category in categories:
                        response += f"• {category.name}\n"
                    response += "\nWhich category interests you?"
                else:
                    response = "We're currently updating our categories. Please check back later!"

            # --- Cart Operations ---
            elif "add" in user_message_clean and "cart" in user_message_clean:
                found = False
                words = user_message_clean.split()

                for product in Product.objects.all():
                    product_name_words = product.name.lower().split()
                    if any(word in words for word in product_name_words) or product.name.lower() in user_message_clean:
                        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                        if not created:
                            cart_item.quantity += 1
                            cart_item.save()
                        response = f"✅ Added {product.name} to your cart! Current quantity: {cart_item.quantity}"
                        found = True
                        break

                if not found:
                    response = "⚠️ I couldn't find that product. Try saying 'search [product name]' to find it first."

            elif "show cart" in user_message_clean or "view cart" in user_message_clean or "my cart" in user_message_clean:
                items = cart.items.all()
                if items.exists():
                    total = sum(item.product.price * item.quantity for item in items)
                    response = "🛒 Your cart:\n"
                    for item in items:
                        response += f"• {item.product.name} (Qty: {item.quantity}) - ${item.product.price * item.quantity}\n"
                    response += f"\n💰 Total: ${total:.2f}"
                    response += "\n\nSay 'checkout' when ready to proceed!"
                else:
                    response = "Your cart is empty. Say 'search [product]' to find items to add!"

            elif "remove" in user_message_clean and "cart" in user_message_clean:
                found = False
                for item in cart.items.all():
                    if item.product.name.lower() in user_message_clean:
                        product_name = item.product.name
                        item.delete()
                        response = f"❌ Removed {product_name} from your cart."
                        found = True
                        break
                if not found:
                    response = "⚠️ Could not find that item in your cart. Say 'show cart' to see current items."

            elif "clear cart" in user_message_clean or "empty cart" in user_message_clean:
                items_count = cart.items.count()
                cart.items.all().delete()
                response = f"🧹 Cart cleared! Removed {items_count} items successfully."

            # --- Checkout ---
            elif "checkout" in user_message_clean or "proceed" in user_message_clean or "buy" in user_message_clean:
                if cart.items.exists():
                    if user and user.is_authenticated:
                        response = "✅ Great! Redirecting you to checkout page. Please complete your order there."
                    else:
                        response = "🔐 Please login first to proceed with checkout. You can login from the top menu."
                else:
                    response = "🛒 Your cart is empty! Add some products first before checkout."

            # --- Help ---
            elif "help" in user_message_clean or "what can you do" in user_message_clean:
                response = """🤖 I can help you with:

- 🔍 Search products: "search laptops" or "find phones"
- 📂 Browse categories: "show categories"
- 🛒 Cart management: "add [product] to cart", "show cart", "remove [product]"
- 💳 Checkout: "checkout" or "proceed to buy"
- ℹ️ General help: just ask me anything!

What would you like to do?"""

            # --- Orders ---
            elif "orders" in user_message_clean or "my orders" in user_message_clean:
                if user and user.is_authenticated:
                    orders = Order.objects.filter(user=user)[:3]
                    if orders:
                        response = "📦 Your recent orders:\n"
                        for order in orders:
                            response += f"• Order #{order.id} - ${order.total_price} ({order.status})\n"
                        response += "\nVisit 'My Orders' page for full details."
                    else:
                        response = "📦 You haven't placed any orders yet. Start shopping!"
                else:
                    response = "🔐 Please login to view your orders."

            return JsonResponse({"reply": response})

        except Exception as e:
            return JsonResponse({"error": f"Something went wrong: {str(e)}"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
# ------------------- Frontend Views -------------------
@login_required
def home_view(request):
    return render(request, 'store/home.html')


@login_required
def product_list_view(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    q = request.GET.get('q')
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))

    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    min_price = request.GET.get('min_price')
    if min_price:
        products = products.filter(price__gte=min_price)

    max_price = request.GET.get('max_price')
    if max_price:
        products = products.filter(price__lte=max_price)

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/product_list.html', {'categories': categories, 'page_obj': page_obj})


@login_required
def product_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/product_list.html',
                  {'categories': categories, 'page_obj': page_obj, 'selected_category': category})


@login_required
def product_detail_view(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'store/product_detail.html', {'product': product})


# ------------------- My Orders -------------------
@login_required
def my_orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/my_orders.html', {'orders': orders})


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


@login_required
def delete_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.delete()
    messages.success(request, "Order removed successfully.")
    return redirect('my-orders')


# ------------------- Checkout -------------------
@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, "Your cart is empty!")
        return redirect('product-list-html')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        shipping_address = request.POST.get('shipping_address')
        payment_method = request.POST.get('payment_method', 'cod')

        total_price = sum(Product.objects.get(id=pid).price * qty for pid, qty in cart.items())

        order = Order.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            shipping_address=shipping_address,
            payment_method=payment_method,
            total_price=total_price,
            status='Processing'
        )

        for pid, qty in cart.items():
            product = Product.objects.get(id=pid)
            OrderItem.objects.create(order=order, product=product, quantity=qty, price=product.price)

        request.session['cart'] = {}
        messages.success(request, "Order placed successfully!")
        return redirect('my-orders')

    return render(request, 'store/checkout.html')


# ------------------- API Views -------------------
class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        category_id = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        return queryset


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'


class ProductCreateAPIView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'


class ProductDeleteAPIView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer