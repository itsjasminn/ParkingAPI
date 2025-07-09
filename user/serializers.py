import json
import random
import re
from datetime import timedelta

from django.contrib.auth.hashers import make_password
from redis import Redis
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer, Serializer

from user.models import User
from user.tasks import send_email


class RegisterModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = 'username', 'email', 'password', 'phone', 'first_name'

    def validate_password(self, value):
        return make_password(value)

    def validate_phone(self, value):
        return re.sub(r'\D', "", value)


class ForgotSerializer(Serializer):
    email = CharField(max_length=255)

    def validate_email(self, value):
        query = User.objects.filter(email=value)
        if not query.exists():
            raise ValidationError("Bunday email topilmadi")
        return value

    def send_code(self):
        redis = Redis(decode_responses=True)
        email = self.validated_data.get("email")
        random_code = random.randrange(10 ** 5, 10 ** 6)
        data = {"code": random_code, "status": "False"}
        data_str = json.dumps(data)
        redis.mset({email: data_str})
        redis.expire(email, time=timedelta(minutes=1))
        send_email(email, f"Code: {random_code}")


class VerifyOTPSerializer(Serializer):
    email = CharField(max_length=255)
    code = CharField(max_length=255)

    def validate(self, attrs):
        redis = Redis(decode_responses=True)
        email = attrs.get("email")
        code = attrs.get("code")
        data_str = redis.mget(email)[0]  # '{"code": ... , "status": ...}'
        if not data_str:
            raise ValidationError("Code expire !")
        data_dict: dict = json.loads(data_str)
        verify_code = data_dict.get('code')
        if str(verify_code) != str(code):
            raise ValidationError("Code xato !")
        redis.mset({email: json.dumps({"status": "True"})})
        redis.expire(email, time=timedelta(minutes=2))
        return attrs


class ChangePasswordSerializer(Serializer):
    email = CharField(max_length=255)
    password = CharField(max_length=255)
    confirm_password = CharField(max_length=255)

    def validate_email(self, value):
        redis = Redis(decode_responses=True)
        data_str = redis.mget(value)[0]  # {"status"}
        if data_str == None:
            raise ValidationError("Email ni tastiqlash kerak !")
        data_dict = json.loads(data_str)
        status = data_dict.get("status", "False")
        if status == "False":
            raise ValidationError("Email ni tastiqlash kerak !")
        redis.delete(value)
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        if password != confirm_password:
            raise ValidationError("password bilan confirm teng emas!")
        attrs['password'] = make_password(password)
        return attrs

    def save(self, **kwargs):
        data = self.validated_data
        email = data.get("email")
        password = data.get("password")
        User.objects.filter(email=email).update(password=password)


class ProfileModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "first_name", "last_name", "username", "phone", "email", "date_joined", "role"
        read_only_fields = "email", "date_joined", "role"

    def validate_phone(self, value):
        return re.sub(r'\D', "", value)
