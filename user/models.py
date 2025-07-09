from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.enums import TextChoices
from django.db.models.fields import CharField


# Create your models here.



class User(AbstractUser):
    class RoleType(TextChoices):
        USER = 'user' , 'User'
        ADMIN = 'admin' , 'Admin'
        SUPER_ADMIN = 'super admin' , 'Super Admin'

    email = models.EmailField(unique=True)
    phone = CharField(max_length=255 , unique=True)
    role = CharField(max_length=60 , choices=RoleType , default=RoleType.USER)
