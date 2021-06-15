from django.db import models
from customer.models import *
# Create your models here.
class HostNotification(models.Model):
    N_id=models.AutoField(primary_key=True)
    N_Host=models.ForeignKey(Host,on_delete=models.CASCADE )
    N_Title=models.CharField(max_length=500,default="")
    N_date_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    N_Description=models.CharField(max_length=500,default="")
    N_status=models.BooleanField(default=True)