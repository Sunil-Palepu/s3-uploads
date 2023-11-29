import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import boto3
from botocore.exceptions import ClientError
from django.core.exceptions import ValidationError
from datetime import datetime
from .models import ModelUploads
from .serializers import UploadSerializer




class InitializingS3:

    @staticmethod
    #method to create a presigned url , initializing the s3_client object
    def create_presigned_url(client_method, object_key, bucket_name=settings.AWS_STORAGE_BUCKET_NAME,  expiration=3600):
        s3_client = boto3.client('s3',
                            aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
                            region_name='ap-south-1'
                            )
       
        try:
            response = s3_client.generate_presigned_url(
            ClientMethod = client_method,
            Params = {
                'Bucket': bucket_name,
                'Key': object_key
            },
            ExpiresIn = expiration
            )
            return response
        except ClientError as e:
            print(f"Error genreating presign url: {e}")
            return None




class S3Upload(APIView):

    #client posts the meta data like file name etc.
    # we should generate a presigned url with meta data
    #response with a presigned url which uploads a file to s3
    def post(self, request, format=None):
       
        try:
            original_name = request.data['file_name'].lower()       #value = sportscar.jpeg
            file_size = request.data['file_size']                   #value = 500
            print(original_name)
            
            if not original_name:
                return Response({'error message':'original_name must contain value'})
            if not file_size:
                return Response({'error message': 'file size must contain a value'})

            #validations
            allowed_formats = ['jpeg', 'jpg']
            allowed_size = 50_000 #in kb
            format = original_name.split('.')[-1].lower()
            
            if format not in allowed_formats:
                return Response({'error': 'Invalid image format'}, status=status.HTTP_400_BAD_REQUEST)
            
            if int(file_size) > allowed_size:
                return Response({'error':f'file size less then {allowed_size} kb'}, status=status.HTTP_400_BAD_REQUEST)



            # Check if the name is already in the database
            if ModelUploads.objects.filter(file_name=original_name).exists():
                return Response({'error': 'File name is already in the database'}, status=status.HTTP_400_BAD_REQUEST)
            
            #saving to database
            instance = ModelUploads(file_name=original_name, file_size=file_size)
            instance.save()

            # bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            datetimevalue = datetime.now()

            object_key = f'images/{datetimevalue}-{original_name}'

            presigned_url = InitializingS3.create_presigned_url(client_method='put_object', object_key=object_key)
     
            if presigned_url:
                instance.object_key = object_key
                instance.save()
                return Response({'presigned_url': presigned_url}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Failed to generate presigned URL'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError:
            return Response({'error': 'Please provide a file_name and filesize  in the request'}, status=status.HTTP_400_BAD_REQUEST)

      


class IsUploaded(APIView):
    
    #update the database entity field isuploaded to True
    def put(self, request, file_name):
        try:
            isuploaded = request.data['isuploaded']
            if not isuploaded or isuploaded != 'True':
                return Response({'error': 'value must be True'})
            print('isuploaded = ', isuploaded)
            file = ModelUploads.objects.get(file_name=file_name)
            print('file = ', file)
            file.is_uploaded = isuploaded
            file.save()
            return Response({'message':'successfully updated the database'})
        except KeyError:
            return Response({'KeyError':'please provide "isuploaded" parameter in the request'})




class DownloadS3File(APIView):
     
     #generating a presigned url to download the file
     def get(self, request, file_name):

        try:
            uploadedfile = ModelUploads.objects.get(file_name=file_name)
            print('uploaded file = ', uploadedfile)
            object_key = uploadedfile.object_key
            print('object key = ',object_key)

            presigned_url = InitializingS3.create_presigned_url('get_object', object_key)
            
            if presigned_url:
                return Response({'presigned_url': presigned_url}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to generate presigned URL'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            return Response({f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
