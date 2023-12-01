from django.db import models

# Create your models here.
class ModelUploads(models.Model):
    object_key= models.CharField(max_length=200)
    file_name = models.CharField(max_length=200)
    file_size = models.IntegerField()
   
