from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password
from datetime import date
import re
import uuid
# Create your models here.


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    password = models.CharField(default="",max_length=120, null=False) 
    username = models.CharField(max_length=40, unique=True, default='')
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    country_code = models.CharField(max_length=4)
    mobile_number = models.CharField(max_length=10)
    account_activated = models.BooleanField(default=False)
    timestamp_lastupdated = models.DateTimeField(auto_now=True)
    timestamp_added = models.DateTimeField(auto_now_add=True)
  
    def __str__(self):
        return self.email
    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)
    
    def clean(self):
        username = self.username.lower()
        if " " in username:
            raise ValidationError("Username cannot contain spaces.")

        if re.match(r"^\d", username):
            raise ValidationError("Username cannot start with a number.")
        

class FriendRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    from_user = models.ForeignKey(User, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_friend_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')







