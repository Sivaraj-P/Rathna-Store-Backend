from rest_framework import serializers
from .models import User
from django.utils import timezone
import re


class UserSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)
    class Meta:
        model=User
        fields=['first_name','last_name','email_id','phone_number','password']

    def validate_password(self,value):
        pw_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+{}|:"<>?])[A-Za-z\d!@#$%^&*()_+{}|:"<>?]{8,}$')
        if not pw_pattern.match(value) or len(value)>30:
            print(value)
            raise serializers.ValidationError('Enter a valid password')
        return value
    
    def create(self,data):
        password=data.pop('password')
        user=User.objects.create(**data)
        user.set_password(password)
        user.save()
        return user
    
