from django.contrib import admin
from .models import Category, Product, ShippingAddress, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'mrp', 'discount_percent', 'price', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at', 'updated_at')
    search_fields = ('name', 'description')

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'city', 'state', 'country', 'pincode', 'landmark', 'contact')
    search_fields = ('user__username', 'address', 'city', 'state', 'country', 'pincode')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'no_of_product', 'payment_method', 'tax_price', 'shipping_price', 'total_price', 'is_paid', 'paid_at', 'delivered_at', 'created_at', 'status')
    list_filter = ('payment_method', 'is_paid', 'created_at', 'status')
    search_fields = ('user__username', 'status')
    date_hierarchy = 'created_at'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'name', 'qty', 'price')
    search_fields = ('product__name', 'order__id', 'name')
