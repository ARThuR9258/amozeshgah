from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.



class User(AbstractUser):
    phone_number = models.CharField(max_length=11, unique=True, null=True, verbose_name='شماره موبایل')
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.email
