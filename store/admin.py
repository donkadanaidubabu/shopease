from django.contrib import admin
from .models import Product, Category, Order, OrderItem

# Existing registrations
admin.site.register(Category)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock')
    search_fields = ('name',)

# ------------------- Order Admin -------------------

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'price')
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_price', 'is_paid')
    list_filter = ('is_paid', 'created_at')
    search_fields = ('user__username',)
    inlines = [OrderItemInline]
