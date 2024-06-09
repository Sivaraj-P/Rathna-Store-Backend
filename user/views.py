from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from .models import User,UserActivationToken,ForgetPasswordOTP
from .serializers import UserSerializer
from .mail import send_user_activation_mail,send_otp_mail
from django.utils import timezone
from django.contrib.auth import authenticate,login
from knox.views import LoginView

import re
import threading

class LoginApiView(LoginView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            
            email_id=request.data.get("email_id")
            password=request.data.get("password")
            if not email_id or not password:
                 return Response({'detail':'Email ID and Password is required'},status=status.HTTP_406_NOT_ACCEPTABLE)
            email_pattern=re.compile(r'^[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*@[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*$')
            pw_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+{}|:"<>?])[A-Za-z\d!@#$%^&*()_+{}|:"<>?]{8,}$')
            if not email_pattern.match(email_id):
                return Response({'detail':'Invalid Email ID format'},status=status.HTTP_406_NOT_ACCEPTABLE)
            if not pw_pattern.match(password) or len(password)>30:
                return Response({'detail':'Invalid Password format'},status=status.HTTP_406_NOT_ACCEPTABLE)
            
            try:
                user=User.objects.get(email_id__icontains=email_id)
                if not user.is_active:
                    return Response({'detail':'Kindly verify your email before login'},status=status.HTTP_406_NOT_ACCEPTABLE)
                auth_user=authenticate(email_id=user.email_id,password=password)
                if auth_user:
                    login(request, user)
                    return super(LoginApiView, self).post(request, format=None)
                else:
                    return Response({'detail':'Invalid Password'},status=status.HTTP_406_NOT_ACCEPTABLE)
            except :
                return Response({'detail':'User not found in the system'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)             
            return Response({'detail':'Something went wrong try again later'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserApiView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        elif self.request.method == 'POST':
            self.permission_classes = [AllowAny]
        return [permission() for permission in self.permission_classes]
    
    def get(self,request):
        try:
            user=UserSerializer(User.objects.get(id=request.user.id)).data
            return Response(user,status=status.HTTP_200_OK)
        except:
            return Response({'detail':'User not found'},status=status.HTTP_404_NOT_FOUND)
    
    def post(self,request):
        try:
            # if User.objects.filter(email_id=request.data["email_id"]).exists():
            #     return Response({'detail':'User already exists with this email'},status=status.HTTP_409_CONFLICT)
            user=UserSerializer(data=request.data)
            if user.is_valid():
                user.save()
                _user=UserActivationToken.objects.create(user=user.instance)
                send_mail=threading.Thread(target=send_user_activation_mail,args=(_user.user.email_id,f"{_user.user.first_name} {_user.user.last_name}",_user.token))
                send_mail.start()
                return Response({"message":"Account created successfully. Kindly complete email verification before proceeding."},status=status.HTTP_201_CREATED)
            else:
                # errors=[]
                # for field_name, field_errors in user.errors.items():
                #     errors.append(f'{field_errors[0]}')
                # return Response({'detail':errors},status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                 return Response(user.errors,status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except :            
            return Response({'detail':'Something went wrong try again later'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ActivateUserApiView(APIView):
    permission_classes=[AllowAny]
    def get(self,request,token):
        try:
            
            user_token=UserActivationToken.objects.get(token=token)
            if user_token.expire_at <timezone.now():
                
                return Response({'detail':'Activation link expired kindly regenerate link'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if user_token.user_status:
                return Response({'detail':'User account already activated'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                user_token.user_status=True
                user_token.activated_at=timezone.now()
                user_token.save()
                user=User.objects.get(id=user_token.user.id)
                user.is_active=True
                user.save()
                
                return Response({'message':'User Account Activated successfully'}, status=status.HTTP_200_OK)
        except:
            
            return Response({'detail':'Something went wrong try again later'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class RegenerateActivationTokenApiView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            email_id=request.data.get('email_id')
            if not email_id:
                
                return Response({'detail':'Email is required'},status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not re.match(r"[^@]+@[^@]+\.[^@]+", email_id):
                
                return Response({'detail': 'Invalid email format'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            try:
                user=User.objects.get(email_id=email_id)
            except:
                return Response({'detail':'No registered user with this email'}, status=status.HTTP_404_NOT_FOUND)
            if user.is_active :
                return Response({'detail':'User Account already activated'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            user_activation_instance=UserActivationToken.objects.get(user_id=user)
            
            if user_activation_instance.expire_at>timezone.now():
                
                return Response({'detail':'Activation link already sent to registered email'}, status=status.HTTP_406_NOT_ACCEPTABLE)

            user_activation_instance.regenerate_token()
            user_activation_instance.save()
            send_mail=threading.Thread(target=send_user_activation_mail,args=(user.email_id,f"{user.first_name} {user.last_name}",user_activation_instance.token))
            send_mail.start()
            return Response({'message':'Activation link sent to registered email'}, status=status.HTTP_200_OK)

            
        except Exception as e:
            print(e)
            return Response({ 'detail':'Something went wrong please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class GenerateOTPApiView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            email_id=request.data.get("email_id")
            if not email_id:
                return Response({'detail': 'Email is required'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email_id):
                
                return Response({'detail': 'Invalid email format'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            try:
                user=User.objects.get(email_id__icontains=email_id)
            except:
                return Response({'detail':'No registered user with this email'}, status=status.HTTP_404_NOT_FOUND)
            user_otp,created=ForgetPasswordOTP.objects.update_or_create(user=user)
            user_otp.save()
            send_mail=threading.Thread(target=send_otp_mail,args=(user.email_id,f"{user.first_name} {user.last_name}",user_otp.otp))
            send_mail.start()
            return Response({'message':'OTP sent to registered email'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({ 'detail':'Something went wrong please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ForgetPasswordApiView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            email_id=request.data.get("email_id")
            otp=request.data.get("otp")
            password=request.data.get("password")
            if not email_id or not otp:
                return Response({'detail': 'Email and OTP is required'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email_id):
                return Response({'detail': 'Invalid email format'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+{}|:"<>?])[A-Za-z\d!@#$%^&*()_+{}|:"<>?]{8,}$',password) or len(password)>30:
                return Response({'detail': 'Invalid password format'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            # if not otp.isdigit() or len(otp)>7:
            #     return Response({'detail': 'Invalid OTP'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            try:
                user=User.objects.get(email_id__icontains=email_id)
            except:
                return Response({'detail':'No registered user with this email'}, status=status.HTTP_404_NOT_FOUND)
            try:
                user_otp=ForgetPasswordOTP.objects.get(user=user,otp=otp)
                if user_otp.expire_at<timezone.now():
                    return Response({'detail':'OTP expired kindly regenerate new one'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                if user_otp.status:
                    return Response({'detail':'OTP already used kindly regenerate new one'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                user.set_password(password)
                user.save()
                user_otp.save(status=True)
                return Response({'message':'Password updated successfully'}, status=status.HTTP_200_OK)
            except:
                return Response({'detail': 'Invalid OTP'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            print(e)
            return Response({ 'detail':'Something went wrong please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)