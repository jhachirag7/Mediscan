from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    image = models.FileField(upload_to='pics', default='media/default.png')
    hash_val=models.CharField(max_length=300,default='default')

    def __str__(self):
        return str(self.user)+'\'s'+' profile'


class Medicine(models.Model):
    wrong_val=models.CharField(max_length=100,default='error')
    right_val=models.CharField(max_length=100,default='error')


class Billing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name=models.CharField(max_length=300,default='default')
    email=models.CharField(max_length=300,default='default')
    address=models.CharField(max_length=500,default='default')
    city=models.CharField(max_length=300,default='default')
    state=models.CharField(max_length=300,default='default')
    zip=models.CharField(max_length=300,default='default')
    namecard=models.CharField(max_length=300,default='default')
    cardnumber=models.CharField(max_length=500,default='default')
    month=models.CharField(max_length=300,default='default')
    year=models.IntegerField()
    cvv=models.IntegerField()
    uuid=models.CharField(max_length=300,default='default',primary_key=True)

    def __str__(self):
            return str(self.uuid)

class order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    uuid=models.CharField(max_length=300,default='default')
    image=models.CharField(max_length=300,default='default')
    name=models.CharField(max_length=300,default='default')
    price=models.FloatField()
    quantity=models.IntegerField()
