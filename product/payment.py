import razorpay
from django.conf import settings

payment_key=settings.PAYMENT_KEY
payment_secret=settings.PAYMENT_SECRET
client = razorpay.Client(auth=(payment_key, payment_secret))


def create_payment(amount):
    order=client.order.create({
            'amount': int(amount) * 100,
            'currency': 'INR',
            'payment_capture': '1'
        })
    return order['id']


def verify_payment(razorpay_order_id,razorpay_payment_id,razorpay_signature):
    status=client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
    return status