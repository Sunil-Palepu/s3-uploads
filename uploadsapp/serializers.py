from rest_framework import serializers
from .models import ModelUploads



class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelUploads
        fields = ['file_name', 'file_size', 'object_key']

        

class S3UploadSerializer(serializers.Serializer):
    original_name = serializers.CharField(max_length=30)
    file_size = serializers.IntegerField()

    def validate(self, data):
        allowed_formats = ['jpg','jpeg']
        name = data.get('original_name')
        extension = name.split('.')[-1]
        print('extension', extension)
        allowed_size = 10_000   #10 mb or 10_000 kb

        if extension not in allowed_formats:
            raise serializers.ValidationError('only jpeg and jpg file extentsions are allowed')
        
        if data.get('file_size') > allowed_size:
            raise serializers.ValidationError(f'file size should be less than {allowed_size} kb')
        
        else:
            return data
        
    



