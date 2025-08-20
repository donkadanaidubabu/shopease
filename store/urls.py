from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    home_view,
    product_list_view,
    product_detail_view,
    product_by_category,
    ProductListAPIView,
    ProductDetailAPIView,
    ProductCreateAPIView,
    ProductUpdateAPIView,
    ProductDeleteAPIView,
    CategoryViewSet,
    my_orders_view,
    order_detail_view,
    delete_order_view,
    chatbot_view,
    chatbot_test_view,
    chatbot_message
)

urlpatterns = [
    # Chatbot Test Page
    path("chatbot/test/", chatbot_test_view, name="chatbot_test"),

    # Chatbot
    path("chatbot/", chatbot_view, name="chatbot"),
    path("api/chatbot/message/", chatbot_message, name="chatbot_api"),

    # Add this new route for the frontend chatbot widget
    path("chat/message/", chatbot_message, name="chat_message"),

    # Frontend Views
    path('', home_view, name='home'),
    path('products/', product_list_view, name='product-list-html'),
    path('products/<int:id>/', product_detail_view, name='product-detail-html'),
    path('products/category/<int:category_id>/', product_by_category, name='product_by_category'),

    # My Orders
    path('my-orders/', my_orders_view, name='my-orders'),
    path('orders/<int:order_id>/', order_detail_view, name='order-detail'),
    path('my-orders/<int:order_id>/delete/', delete_order_view, name='delete-order'),

    # API Views for Products
    path('api/products/', ProductListAPIView.as_view(), name='product-list'),
    path('api/products/<int:id>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('api/products/create/', ProductCreateAPIView.as_view(), name='product-create'),
    path('api/products/<int:id>/update/', ProductUpdateAPIView.as_view(), name='product-update'),
    path('api/products/<int:id>/delete/', ProductDeleteAPIView.as_view(), name='product-delete'),
]

# Category router
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
urlpatterns += router.urls