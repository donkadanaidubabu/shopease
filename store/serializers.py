from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='image_url', required=False)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'image', 'category']
