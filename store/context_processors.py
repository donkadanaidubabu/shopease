from .models import Category
from cart.models import Cart


def categories_processor(request):
    categories = Category.objects.all()
    return {'categories': categories}


def cart_processor(request):
    """Add cart item count to all templates"""
    cart_item_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item_count = sum(item.quantity for item in cart.items.all())
        except Cart.DoesNotExist:
            cart_item_count = 0

    return {'cart_item_count': cart_item_count}