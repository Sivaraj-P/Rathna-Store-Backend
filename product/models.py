from django.db import models
from user.models import User
from django.conf import settings
import os
import random

def category_images(instance, filename):
    path = "category"

    format = f'{instance.name.lower()}.jpg'
    return os.path.join(path, format)


def product_images(instance, filename):
    path = "product"
    format = f'{instance.name.lower()}.jpg'
    return os.path.join(path, format)



def generate_order_id():
    number = ''.join(str(random.randint(0, 9)) for _ in range(16))
    return settings.ORDER_ID_PREFIX+number



ORDER_STATUS=(
    ('Confirmed','Confirmed'),
    ('Shipped','Shipped'),
    ('Delivered','Delivered'),
    ('Cancelled','Cancelled'),
    ('Payment Failed','Payment Failed')
)


PAYMENT_METHODS=(
('COD','COD'),
('Online Payment','Online Payment')
)

class Category(models.Model):
    name=models.CharField(max_length=20)
    image = models.ImageField(upload_to=category_images)

    def __str__(self) -> str:
        return self.name

class Product(models.Model):
    
    name = models.CharField(max_length=200)
    category=models.ForeignKey(Category,on_delete=models.PROTECT)
    image = models.ImageField(upload_to=product_images)
    description = models.CharField(max_length=500,null=True,blank=True)
    mrp = models.DecimalField(max_digits=12,decimal_places=2,)
    discount_percent = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    price = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.mrp and self.price:
            if self.mrp == self.price:
                self.discount_percent=None
            else:
                self.discount_percent = ((self.mrp - self.price) / self.mrp) * 100
        elif self.mrp and self.discount_percent:
            self.price = self.mrp - (self.mrp * self.discount_percent / 100)
        
        super(Product, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.name


class ShippingAddress(models.Model):
    user=models.ForeignKey(User,on_delete=models.PROTECT)
    address = models.CharField(max_length=200)
    city  = models.CharField(max_length=200)
    state=models.CharField(max_length=100,null=True,blank=True)
    country = models.CharField(max_length=200,null=True,blank=True)
    pincode = models.CharField(max_length=200)
    landmark = models.CharField(max_length=200,null=True,blank=True)
    contact=models.IntegerField()


    def __str__(self):
        return str(self.address)



class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    order_id=models.CharField(max_length=18,default=generate_order_id)
    no_of_product=models.IntegerField(null=True,blank=True)
    payment_method = models.CharField(max_length=200,choices=PAYMENT_METHODS)
    tax_price = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    shipping_price = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    total_price = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(auto_now_add=False,null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    shipping_address=models.ForeignKey(ShippingAddress,on_delete=models.SET_NULL,null=True)
    status=models.CharField(max_length=20,choices=ORDER_STATUS,default='Confirmed')
    bill=models.FileField(null=True,blank=True)
    payment_order_id=models.CharField(max_length=200,null=True,blank=True)
    payment_id=models.CharField(max_length=200,null=True,blank=True)
    payment_signature=models.CharField(max_length=200,null=True,blank=True)



    def __str__(self):
        return str(self.created_at)


class OrderItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    order  = models.ForeignKey(Order,on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=200,null=True,blank=True)
    qty = models.IntegerField(null=True,blank=True,default=0)
    price = models.DecimalField(max_digits=12,decimal_places=2,)
    total = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)


    def __str__(self):
        return str(self.name)



