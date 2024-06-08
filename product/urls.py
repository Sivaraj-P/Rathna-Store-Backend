from django.urls import path,re_path
from .views import CategoryApiView,ProductApiView,ShippingAddressApiView,OrderApiView,OrderItemApiView
from .media import serve_media

urlpatterns=[
    path('category', CategoryApiView.as_view(),name='category'),
    path('product',ProductApiView.as_view(),name='product'),
    path('product/<int:id>',ProductApiView.as_view(),name='product_id'),
    path('shipping-address',ShippingAddressApiView.as_view(),name='shipping_address'),
    path('shipping-address/<int:id>',ShippingAddressApiView.as_view(),name='shipping_address_id'),
    path('orders',OrderApiView.as_view(),name='order'),
    path('order-items',OrderItemApiView.as_view(),name='order_item'),
    path('order-items/<int:id>',OrderItemApiView.as_view(),name='order_item_id'),

]
urlpatterns += [
     re_path(r"^media/(?P<path>.*)", serve_media, name="serve_media"),

]