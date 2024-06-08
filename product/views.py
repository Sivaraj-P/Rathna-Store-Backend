from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import Category,Product,ShippingAddress,Order,OrderItem
from .serializers import CategorySerializer,ProductSerializer,ShippingAddressSerializer,OrderProductSerializer,OrderSerializer,OrderItemSerializer
from django.db import transaction
from django.conf import settings
from .bills import generate_pdf_bill
from .mail import send_order_mail
import threading
import os
class CategoryApiView(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        try:
            data=CategorySerializer(Category.objects.all(),many=True,context = {'request':request}).data
            return Response(data,status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({ 'detail':'Something went wrong please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class ProductApiView(APIView):
    permission_classes=[AllowAny]
    def get(self,request,id=None):
        try:
            category=request.query_params.get('category', None)
            if id:
                try:
                    data=ProductSerializer(Product.objects.get(id=id),context = {'request':request}).data
                    return Response(data,status=status.HTTP_200_OK)
                except:
                    return Response({ 'detail':'Invalid product id'}, status=status.HTTP_400_BAD_REQUEST)
            if category:
                data=ProductSerializer(Product.objects.filter(category_id=int(category)),many=True,context = {'request':request}).data
            else:
                data=ProductSerializer(Product.objects.all(),many=True,context = {'request':request}).data
            return Response(data,status=status.HTTP_200_OK)
        except :
            return Response({ 'detail':'Something went wrong please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ShippingAddressApiView(APIView):
    def get(self,request):
        try:
            data=ShippingAddressSerializer(ShippingAddress.objects.filter(user=request.user),many=True).data
            return Response(data,status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({ 'detail':'Something went wrong please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self,request):
        try:
            data=ShippingAddressSerializer(data=request.data)
            if data.is_valid():
                data.save(user=request.user)
                return Response(data.data,status=status.HTTP_200_OK)
            else:
                return Response(data.errors,status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except:
            return Response({ 'detail':'Something went wrong please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self,request,id):
        try:
            sa_list=ShippingAddress.objects.filter(user=request.user).values_list('id',flat=True)
            if id in sa_list:
                data=ShippingAddress.objects.get(id=id)
                data.delete()
                return Response({'message':'Shipping address deleted successfully'},status=status.HTTP_204_NO_CONTENT)
            else:
                return Response ({'detail':'Shipping address not found'},status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({ 'detail':'Something went wrong please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def patch(self,request,id):
        try:
            sa_list=ShippingAddress.objects.filter(user=request.user).values_list('id',flat=True)
            if id in sa_list:
                obj=ShippingAddress.objects.get(id=id)
                data=ShippingAddressSerializer(instance=obj,data=request.data,partial=True)
                if data.is_valid():
                    data.save()
                    return Response(data.data,status=status.HTTP_201_CREATED)
                else:
                    return Response(data.errors,status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            else:
                return Response ({'detail':'Shipping address not found'},status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({ 'detail':'Something went wrong please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderApiView(APIView):
    def get(self,request):
        try:
            page_number = int(request.query_params.get('page', 1))
            page_size = settings.PAGINATION_SIZE

            orders = Order.objects.filter(user=request.user).order_by('-id')
            total_items = orders.count()
            total_pages = (total_items + page_size - 1) // page_size

            start_index = (page_number - 1) * page_size
            end_index = page_number * page_size

            paginated_orders = orders[start_index:end_index]
            serializer = OrderSerializer(paginated_orders, many=True)
            if not serializer.data:
                return Response([], status=status.HTTP_200_OK)
            data = {
                'total_pages': total_pages,
                'page_number': page_number,
                'page_size': page_size,
                'previous_page': page_number - 1 if page_number > 1 else None,
                'next_page': page_number + 1 if page_number < total_pages else None,
                'orders': serializer.data
            }

            
            return Response(data, status=status.HTTP_200_OK)


            # data=OrderSerializer(Order.objects.filter(user=request.user).order_by('-id'),many=True).data
            # return Response(data, status=status.HTTP_200_OK)
        except :
            return Response({ 'detail':'Something went wrong please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderItemApiView(APIView):
    def post(self,request):
        try:
            shipping_address_id=request.data.get("shipping_address_id")
            order_list=request.data.get("order_list")
            if not order_list:
                return Response({"detail":"Order list is required"},status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not shipping_address_id:
                return Response({"detail":"Please select shipping address"},status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            user_shipping_address=ShippingAddress.objects.filter(user=request.user).values_list('id',flat=True)
            if shipping_address_id not in user_shipping_address:
                return Response({"detail":"Invalid shipping address"},status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            ordered_items=OrderProductSerializer(data=order_list,many=True)
            if ordered_items.is_valid():
                with transaction.atomic():
                    order=Order.objects.create(user=request.user,shipping_address_id=shipping_address_id)
                    total_price=0
                    no_of_product=0
                    order_items=[]
                    for item in ordered_items.data:
                        try:
                            product=Product.objects.get(id=item["product_id"])
                            quantity=item["quantity"]
                            order_item=OrderItem.objects.create(product=product,order=order,name=product.name,qty=quantity,price=product.price,total=quantity*product.price)
                            order_items.append(order_item)
                            total_price+=quantity*product.price
                            no_of_product+=1
                        except Exception as e:
                            print(e)   
                    
                    folder_path = os.path.join(settings.MEDIA_ROOT, f'bills/{request.user.email_id}/')
                    os.makedirs(folder_path, exist_ok=True)

                    # Define PDF file path
                    
                    
                    order.total_price=total_price
                    order.no_of_product=no_of_product
                    order.bill=f'bills/{request.user.email_id}/{order.order_id}.pdf'
                    order.save()
                    bill_path = os.path.join(folder_path, f'{order.order_id}.pdf')
                    
                    generate_bill=threading.Thread(target=generate_pdf_bill,args=(order,order_items,bill_path))
                    generate_bill.start()
                    generate_bill.join()
                    send_mail=threading.Thread(target=send_order_mail,args=(request.user.email_id,f"{request.user.first_name} {request.user.last_name}",order))
                    send_mail.start()
                    data=OrderSerializer(order).data
                    return Response(data, status=status.HTTP_201_CREATED)
            else:
               return Response(ordered_items.errors,status=status.HTTP_422_UNPROCESSABLE_ENTITY) 
        except Exception as e:
            print(e)
            return Response({ 'detail':'Something went wrong please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get(self,request,id):
        try:
            order_list=Order.objects.filter(user=request.user)
            if id in order_list.values_list('id',flat=True):
                order=OrderSerializer(order_list.get(id=id),context={"request":request}).data
                products=OrderItemSerializer(OrderItem.objects.filter(order_id=id),many=True,context={"request":request}).data
                data={
                    "order":order,
                    "products":products
                }
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response ({'detail':'Order details not found'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({ 'detail':'Something went wrong please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
