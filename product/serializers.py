from rest_framework import serializers
from .models import Category,Product,ShippingAddress,Order,OrderItem

class CategorySerializer(serializers.ModelSerializer):
    item_count=serializers.SerializerMethodField()

    def get_item_count(self,obj):
        return Product.objects.filter(category__id=obj.id).count()
    class Meta:
        model=Category
        fields='__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name=serializers.ReadOnlyField(source='category.name',read_only=True)
    class Meta:
        model=Product
        fields='__all__'


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model=ShippingAddress
        exclude=['user']


class OrderProductSerializer(serializers.Serializer):
    product_id=serializers.IntegerField()
    quantity=serializers.IntegerField()


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        exclude=['user']

class OrderItemSerializer(serializers.ModelSerializer):
    product_image=serializers.SerializerMethodField()
    def get_product_image(self,obj):
        try:
            request = self.context.get('request', None)
            return request.build_absolute_uri(obj.product.image.url)
        except:
            return None
    class Meta:
        model=OrderItem 
        fields='__all__'       