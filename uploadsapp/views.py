import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from .models import ModelUploads
from .serializers import UploadSerializer, S3UploadSerializer
from django.utils.text import slugify




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
            #updated validations
            serializer = S3UploadSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):   
                
                original_name = serializer.validated_data['original_name']
                format = original_name.split('.')[-1]
                name  = original_name.split('.')[0]

                current_datetime = datetime.now()
                formatted_datetime = current_datetime.strftime("%Y%m%d%H%M%S")

                name = slugify(name)
                object_key = 'user-uploads/' + f'{formatted_datetime}-{name}.{format}'
            
                presigned_url = InitializingS3.create_presigned_url(client_method='put_object', object_key=object_key)
        
                if presigned_url:
                    return Response({'presigned_url': presigned_url, 'object_key':object_key}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': 'Failed to generate presigned URL'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': {str(e)}}, status=status.HTTP_400_BAD_REQUEST)

      


class IsUploaded(APIView):
    
    #update the database with original name and object key
    def post(self, request):
        try:
            print('request.data= ',request.data)
            serializer = UploadSerializer(data=request.data)
            print('serializer = ', serializer)
            if serializer.is_valid(raise_exception=True):
                print('hai')
                serializer.save()   

                return Response({'message':'successfully updated the database', 'serializer.data': serializer.data})
        except KeyError:
            return Response({'KeyError':'please provide required parameters in the request'})




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
                return Response({'presigned_url_to_download_a_file': presigned_url}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to generate presigned URL'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            return Response({f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

