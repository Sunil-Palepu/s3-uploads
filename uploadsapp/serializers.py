from rest_framework import serializers
from .models import ModelUploads


class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelUploads
        fields = ['file_name', 'file_size', 'object_key']

        