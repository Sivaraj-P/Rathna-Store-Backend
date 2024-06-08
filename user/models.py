from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta
import random
import string

Phone_Regex = RegexValidator(regex=r'^\d{10}$', message="Phone number must have 10 digits.")
Name_Regex = RegexValidator(regex=r'^[a-zA-Z ]+$', message="Name should contain only characters and spaces.")
Email_Regex=RegexValidator(regex=r'^[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*@[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*$', message="Enter a valid email address.")


class CustomUserManager(BaseUserManager):
    def create_user(self, email_id, password=None, **extra_fields):
        if not email_id:
            raise ValueError("The Email field must be set")
        email_id = self.normalize_email(email_id)
        user = self.model(email_id=email_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email_id, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    first_name = models.CharField(validators=[Name_Regex],max_length=50,verbose_name = "First Name")
    last_name = models.CharField(validators=[Name_Regex],max_length=50,verbose_name = "Last Name")
    email_id = models.EmailField(validators=[Email_Regex],unique=True, max_length=255,verbose_name = "Email ID")
    phone_number = models.BigIntegerField(validators=[Phone_Regex],verbose_name = "Phone Number")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email_id'
    REQUIRED_FIELDS = ['first_name', 'last_name','phone_number' ]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"



def get_token(length=50):
    characters = string.ascii_letters + string.digits
    token = ''.join(random.choice(characters) for _ in range(length))
    return token

def get_otp(length=7):
    characters = string.digits
    token = ''.join(random.choice(characters) for _ in range(length))
    return token

class UserActivationToken(models.Model):
    user=models.OneToOneField(User,on_delete=models.PROTECT)
    token=models.CharField(max_length=50,default=get_token)
    user_status=models.BooleanField(default=False)
    created_at=models.DateTimeField(null=True,blank=True)
    expire_at=models.DateTimeField(null=True,blank=True)
    activated_at=models.DateTimeField(null=True,blank=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at=timezone.now()
            self.expire_at = self.created_at + timedelta(minutes=15)

        super().save(*args, **kwargs)

    def regenerate_token(self):
        self.token=get_token()
        self.created_at=timezone.now()
        self.expire_at=self.created_at+timedelta(minutes=15)

    
    def __str__(self) -> str:
        return self.user.email_id
    

class ForgetPasswordOTP(models.Model):
    user=models.OneToOneField(User,on_delete=models.PROTECT)
    otp=models.CharField(max_length=50)
    status=models.BooleanField(default=False)
    created_at=models.DateTimeField(null=True,blank=True)
    expire_at=models.DateTimeField(null=True,blank=True)

    def save(self, status=None,*args, **kwargs):
        if status:
            self.status=True
        else:
            self.otp=get_otp()
            self.created_at=timezone.now()
            self.expire_at = self.created_at + timedelta(minutes=10)
            self.status=False

        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.user.email_id