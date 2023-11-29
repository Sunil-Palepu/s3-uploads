from django.db import models

# Create your models here.
class ModelUploads(models.Model):
    object_key= models.CharField(max_length=200)
    file_name = models.CharField(max_length=200)
    file_size = models.CharField(max_length=200,default='something')
    is_uploaded = models.BooleanField(default=False)

    


