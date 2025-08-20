from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import string
from cart.models import Cart, CartItem
from store.models import Product

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
            cart, created = Cart.objects.get_or_create(user=user)

            response = "I didn’t fully understand that. Can you rephrase?"

            # --- Greetings ---
            greetings = ["hi", "hello", "hey"]
            if any(greet in user_message_clean.split() for greet in greetings):
                response = "Hello! 👋 How can I help you today?"

            # --- Bot Logic for Cart and Checkout ---
            elif "add" in user_message_clean and "cart" in user_message_clean:
                found = False
                for product in Product.objects.all():
                    if product.name.lower() in user_message_clean:
                        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                        if not created:
                            cart_item.quantity += 1
                            cart_item.save()
                        response = f"✅ Added {product.name} to your cart!"
                        found = True
                        break
                if not found:
                    # Try partial match
                    for product in Product.objects.all():
                        if product.name.lower().startswith(user_message_clean.split()[-1]):
                            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                            if not created:
                                cart_item.quantity += 1
                                cart_item.save()
                            response = f"✅ Added {product.name} to your cart!"
                            found = True
                            break
                if not found:
                    response = "⚠️ I couldn’t find that product. Please specify the exact or close name."

            elif "show cart" in user_message_clean:
                items = cart.items.all()
                if items.exists():
                    response = "🛒 Your cart:\n"
                    for item in items:
                        response += f"- {item.product.name} ({item.quantity})\n"
                else:
                    response = "Your cart is empty."

            elif "remove" in user_message_clean:
                for item in cart.items.all():
                    if item.product.name.lower() in user_message_clean:
                        item.delete()
                        response = f"❌ Removed {item.product.name} from your cart."
                        break
                else:
                    response = "⚠️ Could not find that item in your cart."

            elif "clear cart" in user_message_clean:
                cart.items.all().delete()
                response = "🧹 Cart cleared successfully!"

            elif "checkout" in user_message_clean or "proceed" in user_message_clean:
                response = "✅ Redirecting you to checkout page soon!"

            return JsonResponse({"reply": response})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=405)
